import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3
from datetime import date, timedelta
import os
from PIL import Image, ImageTk

DB_FILE = "advent.db"
ASSETS_DIR = "assets"
green = "#809059"
peach = "#dba582"
WIDTH = 760
HEIGHT = 360

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
        self.load_viewer_name()
        self._build_ui()
        
    def _load_fonts(self):
        self.title_font = ("Slight", 32, "bold")
        self.small_font = ("Georgia", 16, "bold")

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()   
    
    def show_background_images(self, root):
        pear_img = Image.open("shapes/pears.png")
        pear_img = pear_img.resize((400, int(pear_img.height * 400 / pear_img.width)), Image.Resampling.LANCZOS)
        self.pear_img = ImageTk.PhotoImage(pear_img)

        pear_label = tk.Label(root, image=self.pear_img, bg=green, borderwidth=0, highlightthickness=0)
        pear_label.place(x=10, rely=1.0, anchor="sw")   # bottom-left

        dove_img = Image.open("shapes/dove.png")
        dove_img = dove_img.resize((300, int(dove_img.height * 300 / dove_img.width)), Image.Resampling.LANCZOS)
        self.dove_img = ImageTk.PhotoImage(dove_img)

        dove_label = tk.Label(root, image=self.dove_img, bg=green, borderwidth=0, highlightthickness=0)
        dove_label.place(relx=1.0, y=20, anchor="ne")   # top-right
        
    def round_rect(self, canvas, x1, y1, x2, y2, r=35, **kwargs):
            points = [
                x1+r, y1,
                x2-r, y1,
                x2, y1,
                x2, y1+r,
                x2, y2-r,
                x2, y2,
                x2-r, y2,
                x1+r, y2,
                x1, y2,
                x1, y2-r,
                x1, y1+r,
                x1, y1
            ]
            return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def pill(self, canvas, x1, y1, x2, y2, **kwargs):
            r = (y2 - y1) // 2
            canvas.create_oval(x1, y1, x1 + 2*r, y2, **kwargs)
            canvas.create_oval(x2 - 2*r, y1, x2, y2, **kwargs)
            canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)


    def _build_ui(self):
        root = tk.Frame(self, bg=green)
        root.pack(expand=True, fill="both")
        self.show_background_images(root)

        card = tk.Canvas(root, width=760, height=360, bg=green, highlightthickness=0)
        card.pack(pady=40)
        self.round_rect(card, 20, 20, 740, 340, r=45, fill=peach, outline=peach)

        card.create_text(
            WIDTH/2, 60,
            text=f"{(self.viewer_name).upper()}, YOUR",
            font=("Georgia", 16, "bold"),
            fill="white"
        )

        img = Image.open("shapes/welcome_text.png")
        img = img.resize((600, int(img.height * 600 / img.width)), Image.Resampling.LANCZOS)
        self.welcome_img = ImageTk.PhotoImage(img)

        card.create_image(
            WIDTH/2,           # center X of canvas (760 / 2)
            180,           # center vertically within card
            image=self.welcome_img
        )

        card.create_text(
            WIDTH/2, 280,
            text="IS WAITING FOR YOU",
            font=("Georgia", 16),
            fill="white"
        )

        # Create button
        btn_holder = tk.Canvas(root, width=230, height=70, bg=green, highlightthickness=0)
        btn_holder.pack()

        self.pill(btn_holder, 10, 10, 220, 60, fill=peach, outline=peach)
        
        btn = tk.Button(
            btn_holder, text="OPEN",
            command=self.show_doors_page,
            bg=peach, fg="white",
            font=("Georgia", 16, "bold"),
            relief="flat", activebackground=peach
        )

        btn_holder.create_window(115, 35, window=btn)



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
        self.viewer_name = name

    def show_doors_page(self):
        self.clear_frame()

        root = tk.Frame(self, bg=green)
        root.pack(expand=True, fill="both")
        self.show_background_images(root)

        # Title canvas for testing
        test_frame = tk.Canvas(root, bg="#809059")
        test_frame.pack(side="top", fill="x", pady=10)
        tk.Label(test_frame, text="TODAY'S DATE:", bg="#809059", fg="white").pack(side="left", padx=8)
        self.curr_date_var = tk.StringVar()
        self._update_current_date_display()
        self.curr_date_lbl = tk.Label(test_frame, textvariable=self.curr_date_var, bg="#809059", fg="white")
        self.curr_date_lbl.pack(side="left")

      #  ttk.Label(test_frame, text="For Testing Purposes", background="#809059", foreground="white").pack(side="left", padx=20)
        ttk.Button(test_frame, text="Increment day", command=self.increment_day).pack(side="left", padx=6)

     
        grid = tk.Frame(root, bg="#809059")
        grid.pack(expand=True)

        INDENT_X = 20

        for i in range(12):
            r = i // 4
            c = i % 4
            doornum = i + 1

            btn_canvas = tk.Canvas(grid, width=180, height=180, bg=green, highlightthickness=0)
            btn_canvas.grid(row=r, column=c, padx=INDENT_X, pady=15)

            self.round_rect(btn_canvas, 10, 10, 170, 170, r=40, fill=peach, outline=peach)
            btn_canvas.create_text(90, 90, text=str(doornum), fill="white", font=("Georgia", 32, "bold"))

            btn_canvas.bind("<Button-1>", lambda e, dn=doornum: self.attempt_open_door(dn))


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
            messagebox.showerror("Not available", "Message unavailable!\nCome back later on door's date.\nPress Increment Day to simulate openings.")
            self.show_doors_page()

    def show_door_content(self, door_num):
        self.clear_frame()

        root = tk.Frame(self, bg=green)
        root.pack(expand=True, fill="both")
        self.show_background_images(root)

        c = self.conn.cursor()
        c.execute("SELECT message, image_path, date_day FROM door WHERE door_num = ?", (door_num,))
        row = c.fetchone()
        message, image_path, date_day = (None, None, DOOR_DATES[door_num - 1])
        if row:
            message, image_path, = row[0], row[1]

        top = tk.Label(root, text=f"DOOR {door_num}", font=("Georgia", 35), bg="#809059", fg="white")
        top.pack(pady=8)

        # Date line
        dt = date(self.get_simulated_date().year, 12, date_day)
        suffix = self.ordinal_suffix(dt.day)
        date_lbl = tk.Label(root, text=f"DATE: DECEMBER {dt.day}{suffix}",font=("Georgia", 16), bg="#809059", fg="white")
        date_lbl.pack()

        # If message exists show it; else default message
        if message:
            msg_box = ScrolledText(root, height=8, width=70)
            msg_box.insert(tk.END, message)
            msg_box.configure(state="disabled")
            msg_box.pack(pady=10)
            
        else:
            # default message "Happy Christmas <name>, <number> days left!"
            # number = days until Dec 25 (25 - date)
            days_left = 25 - dt.day
            default_msg = f"Happy Christmas {self.viewer_name}, {days_left} days left!"
            lbl = tk.Label(root, text=default_msg, font=("Georgia", 25), bg="#809059", fg="white")
            lbl.pack(pady=10)

        # Image if exists
        if image_path and os.path.exists(image_path):
            try:
                pil = Image.open(image_path)
                pil.thumbnail((400, 300))
                tkimg = ImageTk.PhotoImage(pil)
                lbl_img = tk.Label(root, image=tkimg, bg="#809059")
                lbl_img.image = tkimg  # keep ref
                lbl_img.pack(pady=10)
            except Exception as e:
                # image can't be opened
                pass
        

        # Create button
        btn_holder = tk.Canvas(root, width=230, height=70, bg=green, highlightthickness=0)
        btn_holder.pack()

        self.pill(btn_holder, 10, 10, 220, 60, fill=peach, outline=peach)

        btn = tk.Button(
            btn_holder, text="DONE",
            command=self.show_doors_page,
            bg=peach, fg="white",
            font=("Georgia", 16, "bold"),
            relief="flat", activebackground=peach
        )

        btn_holder.create_window(115, 35, window=btn)

    def increment_day(self):
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
