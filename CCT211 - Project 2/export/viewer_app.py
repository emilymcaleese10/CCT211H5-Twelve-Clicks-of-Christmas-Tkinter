import argparse, sqlite3, tkinter as tk
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
