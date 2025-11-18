import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3, shutil, os, sys
from pathlib import Path
from datetime import date

DB_NAME = "advent.db"

# ---------- DB ----------
def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER UNIQUE,
            message TEXT
        );
    """)
    # Pre-seed days 1..24 (message empty)
    for d in range(1, 25):
        cur.execute("INSERT OR IGNORE INTO doors(day, message) VALUES (?, ?)", (d, ""))
    con.commit()
    con.close()

def save_message(day: int, message: str):
    con = sqlite3.connect(DB_NAME)
    con.execute("UPDATE doors SET message=? WHERE day=?", (message, day))
    con.commit()
    con.close()

def read_message(day: int) -> str:
    con = sqlite3.connect(DB_NAME)
    row = con.execute("SELECT message FROM doors WHERE day=?", (day,)).fetchone()
    con.close()
    return row[0] if row else ""

def export_viewer():
    """
    Creates export/ with:
      - advent_view.db (read-only target file at runtime)
      - viewer_app.py (viewer-only UI)
      - start_viewer.sh / start_viewer.cmd
    """
    export_dir = Path("export")
    export_dir.mkdir(exist_ok=True)
    media_dir = export_dir / "media"
    media_dir.mkdir(exist_ok=True)  # ready if you add images later

    # Copy DB
    shutil.copyfile(DB_NAME, export_dir / "advent_view.db")

    # Write viewer app
    (export_dir / "viewer_app.py").write_text(VIEWER_CODE, encoding="utf-8")

    # Launch scripts
    (export_dir / "start_viewer.sh").write_text(
        "#!/usr/bin/env bash\npython3 viewer_app.py --db advent_view.db\n", encoding="utf-8"
    )
    (export_dir / "start_viewer.cmd").write_text(
        "python viewer_app.py --db advent_view.db\n", encoding="utf-8"
    )

    messagebox.showinfo(
        "Export complete",
        "Viewer exported to ./export\nSend that folder to your recipient.\nThey can run start_viewer.sh (Mac/Linux) or start_viewer.cmd (Windows).",
    )

# ---------- UI ----------
class EditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advent Editor (Edit-only)")
        self.geometry("420x260")
        self.resizable(False, False)

        tk.Label(self, text="Day (1–24):").grid(row=0, column=0, padx=10, pady=(14, 6), sticky="e")
        self.day_var = tk.StringVar(value="1")
        tk.Spinbox(self, from_=1, to=24, textvariable=self.day_var, width=6).grid(row=0, column=1, padx=10, pady=(14, 6), sticky="w")

        tk.Label(self, text="Message for this day:").grid(row=1, column=0, padx=10, pady=6, sticky="ne")
        self.msg = tk.Text(self, width=34, height=6, wrap="word")
        self.msg.grid(row=1, column=1, padx=10, pady=6, sticky="w")

        btns = tk.Frame(self)
        btns.grid(row=2, column=0, columnspan=2, pady=12)
        tk.Button(btns, text="Load", width=10, command=self.load_day).pack(side="left", padx=6)
        tk.Button(btns, text="Save", width=10, command=self.save_day).pack(side="left", padx=6)
        tk.Button(btns, text="Export Viewer", width=14, command=export_viewer).pack(side="left", padx=6)

        self.columnconfigure(1, weight=1)
        self.load_day()

    def load_day(self):
        d = self._get_day()
        if d is None:
            return
        self.msg.delete("1.0", "end")
        self.msg.insert("1.0", read_message(d))

    def save_day(self):
        d = self._get_day()
        if d is None:
            return
        text = self.msg.get("1.0", "end").strip()
        save_message(d, text)
        messagebox.showinfo("Saved", f"Saved message for Day {d}.")

    def _get_day(self):
        val = self.day_var.get().strip()
        if not val.isdigit():
            messagebox.showerror("Error", "Day must be a number between 1 and 24.")
            return None
        d = int(val)
        if not (1 <= d <= 24):
            messagebox.showerror("Error", "Day must be between 1 and 24.")
            return None
        return d

# ---------- Minimal viewer code stored as a string for export ----------
VIEWER_CODE = r'''import argparse, sqlite3, tkinter as tk
from tkinter import messagebox
import datetime as dt

def open_db_readonly(path: str):
    # Open SQLite in read-only mode so recipients cannot edit content
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)

class ViewerApp(tk.Tk):
    def __init__(self, db_path: str):
        super().__init__()
        self.title("Advent Viewer (Read-only)")
        self.geometry("380x200")
        self.resizable(False, False)
        self.con = open_db_readonly(db_path)

        tk.Label(self, text="Open a day (1–24):").pack(pady=(16, 6))
        self.day_entry = tk.Entry(self, width=8, justify="center")
        self.day_entry.insert(0, "1")
        self.day_entry.pack()
        tk.Button(self, text="Open", command=self.open_day).pack(pady=10)
        self.out = tk.Message(self, text="", width=320)
        self.out.pack(pady=6)

    def open_day(self):
        val = self.day_entry.get().strip()
        if not val.isdigit():
            messagebox.showerror("Error", "Enter a valid number (1–24).")
            return
        d = int(val)
        if not (1 <= d <= 24):
            messagebox.showerror("Error", "Day must be 1–24.")
            return

        # Optional date-lock: uncomment if you want to restrict by current date in December
        # today = dt.date.today()
        # unlock = dt.date(today.year, 12, d)
        # if today < unlock:
        #     self.out.config(text=f"Locked. Opens on {unlock.isoformat()}.")
        #     return

        row = self.con.execute("SELECT message FROM doors WHERE day=?", (d,)).fetchone()
        msg = (row[0] or "").strip() if row else ""
        if msg:
            self.out.config(text=f"🎁 Day {d}: {msg}")
        else:
            self.out.config(text=f"(No message set for Day {d}.)")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="advent_view.db")
    args = p.parse_args()
    app = ViewerApp(args.db)
    app.mainloop()
'''

# ---------- Main ----------
if __name__ == "__main__":
    init_db()
    EditorApp().mainloop()