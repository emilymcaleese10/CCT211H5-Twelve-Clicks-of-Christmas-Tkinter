import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from config import ASSETS_DIR, PEACH
from ui_helpers import round_rect, pill
from database import SqliteRepo


class DoorEditor(tk.Frame):
    """
    door class to create each door window and attach reltated information
    """
    def __init__(self, master, door_num):
        super().__init__(master, bg="white")
        self.master = master
        self.door_num = door_num
        self.repo = SqliteRepo()

        self.pack(expand=True, fill="both")
        self._build_ui()
        self.load_data()

    # ------------------------------ UI ------------------------------
    def _build_ui(self):
        canvas = tk.Canvas(self, width=760, height=500, bg="white", highlightthickness=0)
        canvas.pack(pady=20)

        round_rect(canvas, 10, 10, 750, 480, r=45, fill=PEACH)

        canvas.create_text(
            380, 50, text=f"DOOR {self.door_num}",
            font=("Georgia", 24, "bold"), fill="white"
        )

        canvas.create_text(
            60, 120, text="Message:\n", font=("Georgia", 16, "bold"),
            fill="white", anchor="w"
        )

        self.msg_text = ScrolledText(self, height=6, width=48, font=("Georgia", 14))
        canvas.create_window(380, 200, window=self.msg_text)

        canvas.create_text(
            60, 280, text="\nImage:", font=("Georgia", 16, "bold"),
            fill="white", anchor="w"
        )

        img_frame = tk.Frame(self, bg="white")
        canvas.create_window(380, 340, window=img_frame)

        self.img_var = tk.StringVar()
        entry = tk.Entry(img_frame, textvariable=self.img_var, width=40, font=("Georgia", 14))
        entry.pack(side="left", padx=6)

        tk.Button(
            img_frame, text="Browse...", font=("Georgia", 14, "bold"),
            command=self.browse_image, bg=PEACH, fg="white"
        ).pack(side="left")

        # Button
        btn_holder = tk.Canvas(self, width=230, height=70, bg="white", highlightthickness=0)
        btn_holder.pack()
        pill(btn_holder, 10, 10, 220, 60, fill=PEACH, outline=PEACH)
        create_btn = tk.Button(
            btn_holder, text="SAVE",
            bg=PEACH, fg="white", font=("Georgia", 16, "bold"),
            relief="flat", command=self.save,
            activebackground=PEACH
        )
        btn_holder.create_window(115, 35, window=create_btn)

    def browse_image(self):
        """
        Browse files to find an image to upload for door
        """
        file = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")
            ]
    )
        if file:
            self.img_var.set(file)

    # ------------------------------ DB ------------------------------
    def load_data(self):
        """
        get data related to door from db
        """
        message, img = self.repo.get_door(self.door_num)
        if message:
            self.msg_text.insert("1.0", message)
        if img:
            self.img_var.set(img)

    def save(self):
        """
        take information from user and store in db
        """
        message = self.msg_text.get("1.0", tk.END).strip() or None
        img_path = self.img_var.get().strip() or None

        if img_path and os.path.exists(img_path):
            ext = os.path.splitext(img_path)[1]
            dest = os.path.join(ASSETS_DIR, f"door{self.door_num}{ext}")

            if os.path.exists(dest):
                os.remove(dest)

            shutil.copy(img_path, dest)
            img_path = dest

        self.repo.update_door(self.door_num, message, img_path)
        messagebox.showinfo("Saved", f"Door {self.door_num} saved.")
        self.master.show_doors_page()
