import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import sqlite3
import os
import shutil
from datetime import datetime
from PIL import Image, ImageTk
import subprocess
import sys

DB_FILE = "advent.db"
ASSETS_DIR = "assets"

# Advent mapping: door number -> date (Dec 13..24)
DOOR_DATES = [(13 + i) for i in range(12)]  # [13,14,...,24] iterable

def ensure_db(): # create db
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS viewer (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                 )""")
    c.execute("""CREATE TABLE IF NOT EXISTS door (
                    id INTEGER PRIMARY KEY,
                    door_num INTEGER UNIQUE,
                    date_day INTEGER,
                    message TEXT,
                    image_path TEXT
                 )""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                 )""")
    for i, day in enumerate(DOOR_DATES, start=1):
        c.execute("INSERT OR IGNORE INTO door(door_num, date_day, message, image_path) VALUES (?, ?, ?, ?)",
                  (i, day, None, None))
    conn.commit()
    conn.close()
    os.makedirs(ASSETS_DIR, exist_ok=True)

class EditorApp(tk.Tk): # editor window
    def __init__(self):
        super().__init__()
        self.title("12 CLICKS - Editor")
        self.geometry("900x700")
        self.configure(bg="white")
        self.conn = sqlite3.connect(DB_FILE)
        self._load_fonts()
        self._build_menu()
        self.show_welcome()

    def _load_fonts(self):
        self.title_font = ("Slight", 36, "bold")
        self.small_font = ("Hina-Mincho", 12)

    def _build_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Export Calendar", command=self.export_calendar)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.destroy)
        menubar.add_cascade(label="Menu", menu=filemenu)
        self.config(menu=menubar)

    def clear_frame(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Menu):
                continue
            widget.destroy()    
    
    def show_background_images(self, root):
        tree_img = Image.open("shapes/tree.png")
        tree_img = tree_img.resize((300, int(tree_img.height * 300 / tree_img.width)), Image.Resampling.LANCZOS)
        self.tree_img = ImageTk.PhotoImage(tree_img)

        tree_label = tk.Label(root, image=self.tree_img, bg="white", borderwidth=0, highlightthickness=0)
        tree_label.place(x=10, rely=1.0, anchor="sw")   # bottom-left

        # Star (top right)
        star_img = Image.open("shapes/star.png")
        star_img = star_img.resize((400, int(star_img.height * 400 / star_img.width)), Image.Resampling.LANCZOS)
        self.star_img = ImageTk.PhotoImage(star_img)

        star_label = tk.Label(root, image=self.star_img, bg="white", borderwidth=0, highlightthickness=0)
        star_label.place(relx=1.0, y=10, anchor="ne")   # top-right
    
    def show_welcome(self):
        self.clear_frame()

        root = tk.Frame(self, bg="white")
        root.pack(expand=True, fill="both")
        
        self.show_background_images(root)
    
        card = tk.Canvas(root, width=760, height=360, bg="white", highlightthickness=0)
        card.pack(pady=40)

        def round_rect(x1, y1, x2, y2, r=35, **kwargs):
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
            return card.create_polygon(points, smooth=True, **kwargs)

        peach = "#dba582"

        # Draw rounded rectangle
        round_rect(20, 20, 740, 340, r=45, fill=peach, outline=peach)

        card.create_text(
            380, 70,
            text="YOUR VERY OWN",
            font=("Georgia", 16, "bold"),
            fill="white"
        )

        img = Image.open("shapes/welcome_text.png")
        img = img.resize((600, int(img.height * 600 / img.width)), Image.Resampling.LANCZOS)
        self.welcome_img = ImageTk.PhotoImage(img)

        card.create_image(
            380,           # center X of canvas (760 / 2)
            180,           # center vertically within card
            image=self.welcome_img
        )

        card.create_text(
            380, 280,
            text="IS WAITING FOR YOU",
            font=("Georgia", 16),
            fill="white"
        )

        # Create button
        btn_holder = tk.Canvas(root, width=230, height=70, bg="white", highlightthickness=0)
        btn_holder.pack()

        # Pill shape
        def pill(canvas, x1, y1, x2, y2, **kwargs):
            r = (y2 - y1) // 2
            canvas.create_oval(x1, y1, x1 + 2*r, y2, **kwargs)
            canvas.create_oval(x2 - 2*r, y1, x2, y2, **kwargs)
            canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)

        pill(btn_holder, 10, 10, 220, 60, fill=peach, outline=peach)

        # Real clickable button on top
        btn = tk.Button(
            btn_holder, text="CREATE",
            command=self.show_enter_name,
            bg=peach, fg="white",
            font=("Georgia", 16, "bold"),
            relief="flat", activebackground=peach
        )

        btn_holder.create_window(115, 35, window=btn)


    def show_enter_name(self):
        self.clear_frame()
        frame = tk.Frame(self, bg="white")
        frame.pack(expand=True, fill="both")

        lbl = tk.Label(frame, text="Who is your advent calendar for?", font=self.small_font, bg="white")
        lbl.pack(pady=20)

        self.show_background_images(frame)

        self.name_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.name_var, width=30)
        entry.pack(pady=5)
        entry.focus()

        btn_enter = ttk.Button(frame, text="ENTER", command=self.save_name_and_show_doors)
        btn_enter.pack(pady=10)

    def save_name_and_show_doors(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Required", "Please enter a name.")
            return
        c = self.conn.cursor()
        c.execute("DELETE FROM viewer")
        c.execute("INSERT INTO viewer(name) VALUES (?)", (name,))
        self.conn.commit()
        self.show_doors_page()

    def show_doors_page(self):
        self.clear_frame()
        topbar = tk.Frame(self, bg="white")
        topbar.pack(side="top", fill="x")
        lbl = tk.Label(topbar, text="Doors", font=self.small_font, bg="white")
        lbl.pack(side="left", padx=10, pady=10)

        # Grid area for doors
        grid = tk.Frame(self, bg="white")
        grid.pack(expand=True, fill="both", padx=20, pady=20)

        # 12 doors, 4 columns x 3 rows
        for i in range(12):
            r = i // 4
            c = i % 4
            doornum = i + 1
            btn = tk.Button(grid, text=str(doornum), width=12, height=6,
                            command=lambda dn=doornum: self.open_door_editor(dn))
            btn.grid(row=r, column=c, padx=12, pady=12)

        # Export dropdown (as requested in top-left). Also available in menu.
        export_btn = ttk.Menubutton(topbar, text="Export")
        export_menu = tk.Menu(export_btn, tearoff=0)
        export_menu.add_command(label="Export Calendar", command=self.export_calendar)
        export_btn["menu"] = export_menu
        export_btn.pack(side="left", padx=10)

    def open_door_editor(self, door_num):
        self.clear_frame()
        DoorEditor(self, door_num)
    

    def export_calendar(self):
        # Export flow: ask where to save the exported package and attempt to create standalone viewer executables
        save_dir = filedialog.askdirectory(title="Choose folder to place exported package")
        if not save_dir:
            return

        # Copy viewer.py and DB and assets
        curr_dir = os.path.abspath(os.path.dirname(__file__))
        src_viewer = os.path.join(curr_dir, "viewer.py")
        if not os.path.exists(src_viewer):
            # Writer can't bundle viewer if it's not present; copy a minimal viewer stub
            messagebox.showinfo("Export failed", "viewer.py not found in the same folder as editor.py. "
                                "Place viewer.py next to editor.py and try again.")
            return

        dest_folder = os.path.join(save_dir, f"12_clicks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(dest_folder, exist_ok=True)
        try:
            shutil.copy(src_viewer, os.path.join(dest_folder, "viewer.py"))
            shutil.copy(DB_FILE, os.path.join(dest_folder, DB_FILE))
            # copy assets folder if exists
            if os.path.isdir(ASSETS_DIR):
                shutil.copytree(ASSETS_DIR, os.path.join(dest_folder, ASSETS_DIR))
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to prepare export files: {e}")
            return

        # Try to create platform-specific executables using PyInstaller (optional)
        # NOTE: This attempt may fail if PyInstaller isn't installed or on this environment.
        try:
            # Build for current platform
            cmd = [sys.executable, "-m", "PyInstaller", "--onefile",
                   "--add-data", f"{DB_FILE}{os.pathsep}.",
                   "--add-data", f"{ASSETS_DIR}{os.pathsep}{ASSETS_DIR}",
                   os.path.join(dest_folder, "viewer.py")]
            subprocess.run(cmd, check=True, cwd=dest_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            # If packaging failed, still show success for bundling files; inform user about PyInstaller step.
            messagebox.showinfo("Exported", f"Calendar exported to folder:\n{dest_folder}\n\n"
                            "Note: Creating .exe/.app files requires PyInstaller. To create platform executables, run:\n\n"
                            "pip install pyinstaller\n"
                            f"pyinstaller --onefile --add-data \"{DB_FILE};.\" --add-data \"{ASSETS_DIR};{ASSETS_DIR}\" viewer.py\n\n"
                            "Run these commands in the exported folder on your own machine.")
            return

        messagebox.showinfo("Exported", f"Calendar exported and viewer packaged into:\n{dest_folder}")

    def on_close(self):
        self.conn.close()
        self.destroy()

class DoorEditor(tk.Frame):
    def __init__(self, master: EditorApp, door_num: int):
        super().__init__(master, bg="white")
        self.master = master
        self.door_num = door_num
        self.conn = sqlite3.connect(DB_FILE)
        self.pack(expand=True, fill="both")
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        top_label = tk.Label(self, text=f"DOOR {self.door_num}", font=("Arial", 18, "bold"), bg="white")
        top_label.pack(pady=10)
        self.msg_label = tk.Label(self, text="+ Message", bg="white")
        self.msg_label.pack(anchor="w", padx=20)
        self.msg_text = ScrolledText(self, height=6, width=60)
        self.msg_text.pack(padx=20, pady=5)
        self.img_label = tk.Label(self, text="+ Image", bg="white")
        self.img_label.pack(anchor="w", padx=20)
        img_frame = tk.Frame(self, bg="white")
        img_frame.pack(padx=20, pady=5)
        self.img_path_var = tk.StringVar()
        self.img_entry = ttk.Entry(img_frame, textvariable=self.img_path_var, width=45)
        self.img_entry.pack(side="left")
        btn_browse = ttk.Button(img_frame, text="Browse...", command=self.browse_image)
        btn_browse.pack(side="left", padx=6)
        btn_save = ttk.Button(self, text="Save", command=self.save)
        btn_save.pack(side="left", padx=20, pady=20)
     

    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if path:
            self.img_path_var.set(path)

    def load_data(self):
        c = self.conn.cursor()
        c.execute("SELECT message, image_path FROM door WHERE door_num = ?", (self.door_num,))
        row = c.fetchone()
        if row:
            message, img = row
            if message:
                self.msg_text.delete("1.0", tk.END)
                self.msg_text.insert(tk.END, message)
            if img:
                self.img_path_var.set(img)

    def save(self):
        message = self.msg_text.get("1.0", tk.END).strip() or None
        image_path = self.img_path_var.get().strip() or None
        # If user selected an external image, copy it into assets and store relative path
        if image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1]
            new_name = f"door{self.door_num}{ext}"
            dest = os.path.join(ASSETS_DIR, new_name)
            try:
                shutil.copy(image_path, dest)
                image_path = dest
            except Exception as e:
                image_path = image_path


        c = self.conn.cursor()
        c.execute("UPDATE door SET message = ?, image_path = ? WHERE door_num = ?", (message, image_path, self.door_num))
        self.conn.commit()
        messagebox.showinfo("Saved", f"Door {self.door_num} saved.")

        self.master.show_doors_page()


if __name__ == "__main__":
    ensure_db()
    app = EditorApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
