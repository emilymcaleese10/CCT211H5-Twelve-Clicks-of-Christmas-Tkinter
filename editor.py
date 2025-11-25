import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import sqlite3
import os
import shutil
from datetime import datetime
from PIL import Image, ImageTk
import subprocess
import platform

DB_FILE = "advent.db"
SHAPES_DIR = "shapes"
ASSETS_DIR = "assets"
peach = "#dba582"
WIDTH = 760
HEIGHT = 360

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
        ensure_db()
        self.conn = sqlite3.connect(DB_FILE)
        self._load_fonts()
        self._build_menu()
        self.show_welcome()

    def _load_fonts(self):
        self.title_font = ("Slight", 32, "bold")
        self.small_font = ("Georgia", 16, "bold")

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

        star_img = Image.open("shapes/star.png")
        star_img = star_img.resize((400, int(star_img.height * 400 / star_img.width)), Image.Resampling.LANCZOS)
        self.star_img = ImageTk.PhotoImage(star_img)

        star_label = tk.Label(root, image=self.star_img, bg="white", borderwidth=0, highlightthickness=0)
        star_label.place(relx=1.0, y=10, anchor="ne")   # top-right

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

    def show_welcome(self):
        self.clear_frame()

        root = tk.Frame(self, bg="white")
        root.pack(expand=True, fill="both")
        
        self.show_background_images(root)
    
        card = tk.Canvas(root, width=760, height=360, bg="white", highlightthickness=0)
        card.pack(pady=40)

        # Draw rounded rectangle
        self.round_rect(card, 20, 20, 740, 340, r=45, fill=peach, outline=peach)

        card.create_text(
            WIDTH/2, 70,
            text="YOUR VERY OWN",
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
        btn_holder = tk.Canvas(root, width=230, height=70, bg="white", highlightthickness=0)
        btn_holder.pack()

        self.pill(btn_holder, 10, 10, 220, 60, fill=peach, outline=peach)

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

        self.show_background_images(frame)
        card = tk.Canvas(frame, width=700, height=360, bg="white", highlightthickness=0)
        card.pack(pady=40)

        self.round_rect(card, 10, 10, 690, 250, r=45, fill=peach, outline=peach)

        card.create_text(
            380, 70,
            text="WHO IS YOUR ADVENT CALENDAR FOR?",
            font=("Georgia", 16, "bold"),
            fill="white"
        )

        # Input bar
        self.name_var = tk.StringVar()
        style = ttk.Style()
        style.configure("Large.TEntry", padding=10, font=("Georgia", 16))
        entry = ttk.Entry(card, textvariable=self.name_var, width=50, style="Large.TEntry")
        card.create_window(WIDTH/2, 150, window=entry)
        entry.focus()

        # Button
        btn_holder = tk.Canvas(frame, width=230, height=70, bg="white", highlightthickness=0)
        btn_holder.pack()

        self.pill(btn_holder, 10, 10, 220, 60, fill=peach, outline=peach)

        # Real clickable button on top
        btn = tk.Button(
            btn_holder, text="SAVE",
            command=self.save_name_and_show_doors,
            bg=peach, fg="white",
            font=("Georgia", 16, "bold"),
            relief="flat", activebackground=peach
        )

        btn_holder.create_window(115, 35, window=btn)

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
        frame = tk.Frame(self, bg="white")
        frame.pack(expand=True, fill="both")
        self.show_background_images(frame)

        # TOP BAR (export button/title)
        top_bar = tk.Frame(frame, bg="white")
        top_bar.pack(fill="x")
        export_btn = ttk.Menubutton(top_bar, text="Export")
        export_menu = tk.Menu(export_btn, tearoff=0)
        export_menu.add_command(label="Export Calendar", command=self.export_calendar)
        export_btn["menu"] = export_menu
        export_btn.pack(side="left", padx=10)

        title = tk.Label(top_bar, 
                         text="Edit Calendar",
                         font=("Georgia", 30), bg="white", padx=50, pady=20)
        title.pack(side="left")

        # GRID
        center = tk.Frame(frame, bg="white")
        center.pack(expand=True)
        grid = tk.Frame(center, bg="white")
        grid.pack()

        INDENT_X = 20

        for i in range(12):
            r = i // 4
            c = i % 4
            doornum = i + 1

            btn_canvas = tk.Canvas(grid, width=180, height=180, bg="white", highlightthickness=0)
            btn_canvas.grid(row=r, column=c, padx=INDENT_X, pady=15)

            self.round_rect(btn_canvas, 10, 10, 170, 170, r=40, fill=peach, outline=peach)
            btn_canvas.create_text(90, 90, text=str(doornum), fill="white", font=("Georgia", 32, "bold"))

            btn_canvas.bind("<Button-1>", lambda e, dn=doornum: self.open_door_editor(dn))

    def open_door_editor(self, door_num):
        self.clear_frame()
        DoorEditor(self, door_num)

    def export_calendar(self):

        # Ask user for export location
        save_dir = filedialog.askdirectory(title="Choose folder to place exported package")
        if not save_dir:
            return

        curr_dir = os.path.abspath(os.path.dirname(__file__))
        src_viewer = os.path.join(curr_dir, "viewer.py")

        if not os.path.exists(src_viewer):
            messagebox.showinfo(
                "Export failed",
                "viewer.py not found next to editor.py.\n"
                "Place viewer.py next to editor.py and try again."
            )
            return

        # Output names
        exe_name = "RUN.exe"
        app_name = "RUN.app"

        # Build export directory
        dest_folder = os.path.join(
            save_dir,
            f"12 Clicks Export {datetime.now().strftime('%d_%m_%Y - %H_%M_%S')}"
        )
        os.makedirs(dest_folder, exist_ok=True)

        try:
            # Copy viewer.py
            shutil.copy(src_viewer, os.path.join(dest_folder, "viewer.py"))

            # Copy DB
            shutil.copy(DB_FILE, os.path.join(dest_folder, DB_FILE))

            # Copy assets
            if os.path.isdir(ASSETS_DIR):
                shutil.copytree(ASSETS_DIR, os.path.join(dest_folder, ASSETS_DIR))

            
            if os.path.isdir(SHAPES_DIR):
                shutil.copytree(SHAPES_DIR, os.path.join(dest_folder, SHAPES_DIR))

            # --- Create helper scripts (optional) ---
            bat_path = os.path.join(dest_folder, "windows.bat")
            with open(bat_path, "w") as bat:
                bat.write(
                    "@echo off\n"
                    "echo Launching Advent Calendar Viewer...\n"
                    "python viewer.py\n"
                    "pause\n"
                )

            sh_path = os.path.join(dest_folder, "mac.sh")
            with open(sh_path, "w") as sh:
                sh.write(
                    "#!/bin/bash\n"
                    "echo \"Launching Advent Calendar Viewer...\"\n"
                    "python3 viewer.py\n"
                )
            try:
                os.chmod(sh_path, 0o755)
            except:
                pass


            system = platform.system()
            pyinstaller_cmd = shutil.which("pyinstaller")

            if not pyinstaller_cmd:
                messagebox.showwarning(
                    "Executable Not Built",
                    "PyInstaller is not installed.\n\n"
                    "Export includes viewer.py and run scripts, but no standalone app.\n\n"
                    "Install PyInstaller to enable automatic .exe/.app creation:\n"
                    "    pip install pyinstaller"
                )
                return

            # Inform user
            messagebox.showinfo(
                "Building Executable",
                "Creating .exe/.app using PyInstaller…\nThis may take 30–60 seconds."
            )

            # Temporary build folder
            temp_build_dir = os.path.join(dest_folder, "build_temp")
            os.makedirs(temp_build_dir, exist_ok=True)

            # Run PyInstaller
            subprocess.run(
                [
                    pyinstaller_cmd,
                    "--onefile",
                    "--windowed",
                    "--name", exe_name.replace(".exe", ""),  # Base name for both .exe and .app
                    "--distpath", temp_build_dir,
                    "--workpath", os.path.join(temp_build_dir, "build"),
                    "--specpath", os.path.join(temp_build_dir, "spec"),
                    os.path.join(dest_folder, "viewer.py")
                ],
                check=False
            )

        
            if system == "Windows":
                built_exe = os.path.join(
                    temp_build_dir,
                    exe_name  # RUN.exe
                )
                if os.path.exists(built_exe):
                    shutil.move(built_exe, os.path.join(dest_folder, exe_name))

            elif system == "Darwin":  # macOS
                built_app = os.path.join(
                    temp_build_dir,
                    app_name  # RUN.app
                )
                if os.path.exists(built_app):
                    shutil.move(built_app, os.path.join(dest_folder, app_name))

            # Clean up temp build folder
            shutil.rmtree(temp_build_dir, ignore_errors=True)

        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export files:\n{e}")
            return

        # Success message
        messagebox.showinfo(
            "Export complete",
            "Calendar exported successfully\n"
            "The viewer application has been created!"
        )



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
        self.canvas = tk.Canvas(self, width=760, height=500, bg="white", highlightthickness=0)
        self.canvas.pack(pady=20)

        self.master.round_rect(self.canvas, 10, 10, 750, 480, r=45, fill=peach, outline=peach)

        self.canvas.create_text(
            380, 50,
            text=f"DOOR {self.door_num}",
            font=("Georgia", 24, "bold"),
            fill="white"
        )

        self.canvas.create_text(
            60, 120,
            text="Message:\n",
            font=("Georgia", 16, "bold"),
            fill="white",
            anchor="w",
        )

        self.msg_text = ScrolledText(self, height=6, width=48, font=("Georgia", 14))
        self.canvas.create_window(380, 200, window=self.msg_text)

        # Image
        self.canvas.create_text(
            60, 280,
            text="\nImage:",
            font=("Georgia", 16, "bold"),
            fill="white",
            anchor="w"
        )

        # Image input and browse button
        img_frame = tk.Frame(self, bg="white")
        self.canvas.create_window(380, 340, window=img_frame)

        self.img_path_var = tk.StringVar()
        self.img_entry = ttk.Entry(img_frame, textvariable=self.img_path_var,
                                    width=40, font=("Georgia", 14))
        self.img_entry.pack(side="left", padx=(0,6))
        btn_browse = tk.Button(img_frame,
                               text="Browse...",
                               command=self.browse_image,
                               bg=peach, fg="white", font=("Georgia", 14, "bold"),
                               activebackground=peach)
        btn_browse.pack(side="left")

        # Save button
        btn_save = tk.Button(self, text="Save", command=self.save,
                              bg=peach, fg="white", font=("Georgia", 16, "bold"),
                              activebackground=peach)
        self.canvas.create_window(380, 450, window=btn_save)



    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=
                                          [("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
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
                pass


        c = self.conn.cursor()
        c.execute("UPDATE door SET message = ?, image_path = ? WHERE door_num = ?",
                  (message, image_path, self.door_num))
        self.conn.commit()
        messagebox.showinfo("Saved", f"Door {self.door_num} saved.")

        self.master.show_doors_page()


if __name__ == "__main__":
    app = EditorApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
