import os
import shutil
import platform
import subprocess
from datetime import datetime
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from config import (
    DB_FILE,
    SHAPES_DIR,
    ASSETS_DIR,
    PEACH,
    WINDOW_WIDTH
)
from database import SqliteRepo
from ui_helpers import round_rect, pill
from door_editor import DoorEditor


class EditorApp(tk.Tk):
    """Main editor window for editing the 12-door advent calendar."""

    def __init__(self):
        super().__init__()
        self.title("12 CLICKS - Editor")
        self.geometry("900x700")
        self.configure(bg="white")

        self.repo = SqliteRepo()
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
        """
        Used for any window to clear page for new content
        """
        for widget in self.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()

    def show_background_images(self, root):
        """
        reused for all pages, shows the two background images of the tree and star
        """
        tree = Image.open(os.path.join(SHAPES_DIR, "tree.png"))
        tree = tree.resize((300, int(tree.height * 300 / tree.width)), Image.Resampling.LANCZOS)
        self.tree_img = ImageTk.PhotoImage(tree)
        tk.Label(root, image=self.tree_img, bg="white").place(x=10, rely=1.0, anchor="sw")

        star = Image.open(os.path.join(SHAPES_DIR, "star.png"))
        star = star.resize((400, int(star.height * 400 / star.width)), Image.Resampling.LANCZOS)
        self.star_img = ImageTk.PhotoImage(star)
        tk.Label(root, image=self.star_img, bg="white").place(relx=1.0, y=60, anchor="ne")

    # ------------ Pages --------------------

    def show_welcome(self):
        """
        Introductory page that displays project title
        """
        self.clear_frame()
        frame = tk.Frame(self, bg="white")
        frame.pack(expand=True, fill="both")
        self.show_background_images(frame)

        card = tk.Canvas(frame, width=WINDOW_WIDTH, height=360, bg="white", highlightthickness=0)
        card.pack(pady=40)
        round_rect(card, 20, 20, 740, 340, r=45, fill=PEACH, outline=PEACH)

        card.create_text(
            WINDOW_WIDTH/2, 70,
            text="YOUR VERY OWN",
            font=("Georgia", 16, "bold"),
            fill="white"
        )

        img = Image.open(os.path.join(SHAPES_DIR, "welcome_text.png"))
        img = img.resize((600, int(img.height * 600 / img.width)), Image.Resampling.LANCZOS)
        self.welcome_img = ImageTk.PhotoImage(img)
        card.create_image(WINDOW_WIDTH/2, 180, image=self.welcome_img)

        card.create_text(
            WINDOW_WIDTH/2, 280,
            text="IS WAITING FOR YOU",
            font=("Georgia", 16),
            fill="white"
        )

        # Button
        btn_holder = tk.Canvas(frame, width=230, height=70, bg="white", highlightthickness=0)
        btn_holder.pack()
        pill(btn_holder, 10, 10, 220, 60, fill=PEACH, outline=PEACH)
        text_id = btn_holder.create_text(
            115, 35,
            text="NEXT",
            fill="white",
            font=("Georgia", 16, "bold")
        )
        btn_holder.bind("<Button-1>", lambda e: self.show_name_page())

    def show_name_page(self):
        """
        Page that prompts user to enter name for their calendar
        """
        self.clear_frame()
        frame = tk.Frame(self, bg="white")
        frame.pack(expand=True, fill="both")
        self.show_background_images(frame)

        card_width = 700
        card_height = 260

        card = tk.Canvas(frame, width=card_width, height=card_height, bg="white", highlightthickness=0)
        card.pack(pady=40)
        round_rect(card, 10, 10, card_width - 10, card_height - 10, r=45, fill=PEACH, outline=PEACH)


        card.create_text(
            card_width // 2,
            70,
            text="WHO IS YOUR ADVENT CALENDAR FOR?",
            font=("Georgia", 16, "bold"),
            fill="white"
        )

        # Entry field
        self.name_var = tk.StringVar()
        style = ttk.Style()
        style.configure("Large.TEntry", padding=10, font=("Georgia", 16))

        entry = ttk.Entry(card, textvariable=self.name_var, width=40, font=("Georgia", 16))


        card.create_window(card_width // 2, 150, window=entry)
        entry.focus()

        # Button
        btn_holder = tk.Canvas(frame, width=230, height=70, bg="white", highlightthickness=0)
        btn_holder.pack()
        pill(btn_holder, 10, 10, 220, 60, fill=PEACH, outline=PEACH)
        text_id = btn_holder.create_text(
            115, 35,
            text="SAVE",
            fill="white",
            font=("Georgia", 16, "bold")
        )
        btn_holder.bind("<Button-1>", lambda e: self.save_name_and_show_doors())

    def save_name_and_show_doors(self):
        """
        store name in db and brings user to main page with door grid
        """
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Required", "Please enter a name.")
            return
        self.repo.set_viewer_name(name)
        self.show_doors_page()

    def show_doors_page(self):
        """
        The actual code that shows the doors grid
        """
        self.clear_frame()

        frame = tk.Frame(self, bg="white")
        frame.pack(expand=True, fill="both")
        self.show_background_images(frame)

        top_bar = tk.Frame(frame, bg="white")
        top_bar.pack(fill="x")
        img = Image.open(os.path.join(SHAPES_DIR, "edit_calendar.png"))
        img = img.resize((600, int(img.height * 600 / img.width)), Image.Resampling.LANCZOS)
        self.title_img = ImageTk.PhotoImage(img)

        export_btn = ttk.Menubutton(top_bar, text="Export")
        menu = tk.Menu(export_btn, tearoff=0)
        menu.add_command(label="Export Calendar", command=self.export_calendar)
        export_btn["menu"] = menu
        export_btn.pack(side="left", padx=10)

        try:
            tk.Label(top_bar, image=self.title_img, bg="white") \
                .pack(side="left", padx=20)
        except AttributeError:
            # Fallback if the image object isn't defined
            tk.Label(top_bar, text="Edit Calendar (Image not loaded)",
                        font=("Georgia", 30), bg="white") \
                        .pack(side="left", padx=20)

        grid_container = tk.Frame(frame, bg="white")
        grid_container.pack(expand=True)

        for i in range(12):
            r, c = divmod(i, 4)
            doornum = i + 1

            door_canvas = tk.Canvas(
                grid_container, width=180, height=180,
                bg="white", highlightthickness=0
            )
            door_canvas.grid(row=r, column=c, padx=15, pady=15)

            round_rect(door_canvas, 10, 10, 170, 170, r=40, fill=PEACH)
            door_canvas.create_text(90, 90, text=str(doornum), fill="white",
                                    font=("Georgia", 32, "bold"))
            door_canvas.bind("<Button-1>", lambda e, n=doornum: self.open_door_editor(n))

    def open_door_editor(self, door_num: int):
        """
        Create door editor object
        """
        self.clear_frame()
        DoorEditor(self, door_num)

    # ------------------------------ Export -------------------------
    def export_calendar(self):
        """
        Exports calendar into file containing .exe or .app file that user's friend can open
        """
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
            # copy information into folder
            shutil.copy(src_viewer, os.path.join(dest_folder, "viewer.py"))

            shutil.copy(DB_FILE, os.path.join(dest_folder, os.path.basename(DB_FILE)))

            if os.path.isdir(ASSETS_DIR):
                shutil.copytree(ASSETS_DIR, os.path.join(dest_folder, "assets"))


            if os.path.isdir(SHAPES_DIR):
                shutil.copytree(SHAPES_DIR, os.path.join(dest_folder, "shapes"))

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
        self.repo.close()
        self.destroy()


if __name__ == "__main__":
    app = EditorApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
