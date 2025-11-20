import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3
from datetime import date, datetime, timedelta
import os
from PIL import Image, ImageTk

DB_FILE = "advent.db"
ASSETS_DIR = "assets"

# door 1 -> Dec 13, door 12 -> Dec 24
DOOR_DATES = [(13 + i) for i in range(12)]

def ensure_db_present():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS viewer (id INTEGER PRIMARY KEY, name TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS door (id INTEGER PRIMARY KEY, door_num INTEGER UNIQUE, date_day INTEGER, message TEXT, image_path TEXT)""")
        for i, day in enumerate(DOOR_DATES, start=1):
            c.execute("INSERT OR IGNORE INTO door(door_num, date_day, message, image_path) VALUES (?, ?, ?, ?)",
                      (i, day, None, None))
        conn.commit()
        conn.close()

class ViewerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("12 CLICKS - Viewer")
        self.geometry("900x700")
        self.configure(bg="#809059")
        ensure_db_present()
        self.conn = sqlite3.connect(DB_FILE)
        self._load_fonts()
        self.sim_day_offset = 0  # 0 means real current date
        self._build_ui()
        self.load_viewer_name()

    def _load_fonts(self):
        self.title_font = ("Slight", 32, "bold")
        self.small_font = ("Hina-Mincho", 12)

    def _build_ui(self):
        # Top area: viewer name and OPEN button
        top_frame = tk.Frame(self, bg="#809059")
        top_frame.pack(side="top", fill="x", pady=12)

        self.name_label = tk.Label(top_frame, text="", font=self.title_font, bg="#809059", fg="white")
        self.name_label.pack(side="left", padx=20)

        btn_open = ttk.Button(top_frame, text="OPEN", command=self.show_doors_page)
        btn_open.pack(side="right", padx=20)

        # For testing: Increment day dropdown
        test_frame = tk.Frame(self, bg="#809059")
        test_frame.pack(side="top", fill="x", pady=4)
        tk.Label(test_frame, text="TODAY'S DATE:", bg="#809059", fg="white").pack(side="left", padx=8)
        self.curr_date_var = tk.StringVar()
        self._update_current_date_display()
        self.curr_date_lbl = tk.Label(test_frame, textvariable=self.curr_date_var, bg="#809059", fg="white")
        self.curr_date_lbl.pack(side="left")

        ttk.Label(test_frame, text="For Testing Purposes", background="#809059", foreground="white").pack(side="left", padx=20)
        ttk.Button(test_frame, text="Increment day", command=self.increment_day).pack(side="left", padx=6)

        # A frame that will hold the dynamic content (doors or door content)
        self.content_frame = tk.Frame(self, bg="#809059")
        self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Start on landing
        self.show_landing()

    def _update_current_date_display(self):
        # Current real date + sim offset
        today = date.today() + timedelta(days=self.sim_day_offset)
        # Show like "DECEMBER 13th"
        day_suffix = self.ordinal_suffix(today.day)
        self.curr_date_var.set(today.strftime(f"%B %d{day_suffix}"))

    @staticmethod
    def ordinal_suffix(n):
        # basic suffix
        if 10 <= (n % 100) <= 20:
            return "th"
        if n % 10 == 1:
            return "st"
        if n % 10 == 2:
            return "nd"
        if n % 10 == 3:
            return "rd"
        return "th"

    def load_viewer_name(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM viewer LIMIT 1")
        row = c.fetchone()
        name = row[0] if row and row[0] else "YOUR"
        self.name_label.config(text=f"{name}, YOUR")
        self.viewer_name = name

    def show_landing(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        lbl = tk.Label(self.content_frame, text=f"{self.viewer_name}, YOUR VERY OWN IS WAITING FOR YOU", font=self.small_font, bg="#809059", fg="white")
        lbl.pack(expand=True)

    def show_doors_page(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

        grid = tk.Frame(self.content_frame, bg="#809059")
        grid.pack(expand=True)

        for i in range(12):
            r = i // 4
            c = i % 4
            door_num = i + 1
            btn = tk.Button(grid, text=str(door_num), width=12, height=6,
                            command=lambda dn=door_num: self.attempt_open_door(dn))
            btn.grid(row=r, column=c, padx=12, pady=12)

    def get_simulated_date(self):
        return date.today() + timedelta(days=self.sim_day_offset)

    def door_unlock_date(self, door_num):
        # returns a date object for the door's unlock date in the current year
        yr = date.today().year
        day = DOOR_DATES[door_num - 1]
        return date(yr, 12, day)

    def attempt_open_door(self, door_num):
        today = self.get_simulated_date()
        unlock = self.door_unlock_date(door_num)
        if today >= unlock:
            self.show_door_content(door_num)
        else:
            messagebox.showerror("Not available", "Message unavailable!\nCome back later on door's date")
            self.show_doors_page()

    def show_door_content(self, door_num):
        for w in self.content_frame.winfo_children():
            w.destroy()

        c = self.conn.cursor()
        c.execute("SELECT message, image_path, date_day FROM door WHERE door_num = ?", (door_num,))
        row = c.fetchone()
        message, image_path, date_day = (None, None, DOOR_DATES[door_num - 1])
        if row:
            message, image_path, = row[0], row[1]

        top = tk.Label(self.content_frame, text=f"DOOR {door_num}", font=("Arial", 16, "bold"), bg="#809059", fg="white")
        top.pack(pady=8)

        # Date line
        dt = date(self.get_simulated_date().year, 12, date_day)
        suffix = self.ordinal_suffix(dt.day)
        date_lbl = tk.Label(self.content_frame, text=f"DATE: DECEMBER {dt.day}{suffix}", bg="#809059", fg="white")
        date_lbl.pack()

        # If message exists show it; else default message
        if message:
            msg_box = ScrolledText(self.content_frame, height=8, width=70)
            msg_box.insert(tk.END, message)
            msg_box.configure(state="disabled")
            msg_box.pack(pady=10)
        else:
            # default message "Happy Christmas <name>, <number> days left!"
            # number = days until Dec 25 (25 - date)
            days_left = 25 - dt.day
            default_msg = f"Happy Christmas {self.viewer_name}, {days_left} days left!"
            lbl = tk.Label(self.content_frame, text=default_msg, bg="#809059", fg="white")
            lbl.pack(pady=10)

        # Image if exists
        if image_path and os.path.exists(image_path):
            try:
                pil = Image.open(image_path)
                pil.thumbnail((400, 300))
                tkimg = ImageTk.PhotoImage(pil)
                lbl_img = tk.Label(self.content_frame, image=tkimg, bg="#809059")
                lbl_img.image = tkimg  # keep ref
                lbl_img.pack(pady=10)
            except Exception as e:
                # image can't be opened
                pass

        btn_done = ttk.Button(self.content_frame, text="DONE", command=self.show_doors_page)
        btn_done.pack(pady=12)

    def increment_day(self):
        # For testing: increment simulated day to next Advent start date then onward.
        # If currently at real today, the spec asked: increment once -> Dec 13, increment again -> Dec 14 etc.
        # We'll set sim_day_offset so the simulated date becomes Dec 13 of this year or move forward by one day.
        current = self.get_simulated_date()
        yr = current.year
        dec13 = date(yr, 12, 13)
        if current < dec13:
            # set to Dec 13
            delta = (dec13 - date.today()).days
            self.sim_day_offset = delta
        else:
            # increment simulated day by 1
            self.sim_day_offset += 1
        self._update_current_date_display()
        messagebox.showinfo("Date changed", f"Simulated date set to {self.get_simulated_date().strftime('%B %d')}")
        # The spec also asked to store dates in DB accordingly. We'll store the simulated offset in settings table.
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("sim_day_offset", str(self.sim_day_offset)))
        self.conn.commit()

    def on_close(self):
        self.conn.close()
        self.destroy()

if __name__ == "__main__":
    app = ViewerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
