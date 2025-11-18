import tkinter as tk
from tkinter import messagebox, filedialog

class SundaeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sundae Builder")
        self.geometry("480x320")

        # State
        self.flavor = tk.StringVar(value="")
        self.syrup = tk.StringVar(value="")
        self.toppings = {
            "Chocolate chips": tk.BooleanVar(value=False),
            "Sprinkles": tk.BooleanVar(value=False),
            "Nuts": tk.BooleanVar(value=False),
            "Peppermint": tk.BooleanVar(value=False),
        }

        # Start window
        self.display = tk.Label(
            self,
            text="Customize your sundae! 🍦",
            font=("Helvetica", 14),
            wraplength=420,
            justify="center"
        )
        self.display.place(relx=0.5, rely=0.5, anchor="center")

        # Menu Bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Choices in Menu Bar
        choices_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Choices", menu=choices_menu)

        # Flavor submenu
        flavor_menu = tk.Menu(choices_menu, tearoff=False)
        for f in ("Chocolate", "Strawberry", "Vanilla"):
            flavor_menu.add_radiobutton(
                label=f, variable=self.flavor, value=f, command=self.update_order
            )
        choices_menu.add_cascade(label="Flavor", menu=flavor_menu)

        # Toppings submenu
        toppings_menu = tk.Menu(choices_menu, tearoff=False)
        for t, var in self.toppings.items():
            toppings_menu.add_checkbutton(
                label=t, variable=var, command=self.update_order
            )
        choices_menu.add_cascade(label="Toppings", menu=toppings_menu)

        # Syrup submenu
        syrup_menu = tk.Menu(choices_menu, tearoff=False)
        for s in ("Chocolate", "Butterscotch", "Berry"):
            syrup_menu.add_radiobutton(
                label=s, variable=self.syrup, value=s, command=self.update_order
            )
        choices_menu.add_cascade(label="Syrup", menu=syrup_menu)

        # Actions menu
        actions_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Actions", menu=actions_menu)
        actions_menu.add_command(label="Save...", command=self.save_order)
        actions_menu.add_separator()
        actions_menu.add_command(label="Clear", command=self.clear_order)
        actions_menu.add_command(label="Quit", command=self.quit_app)

    def make_order_string(self):
        # If nothing selected yet
        if not self.flavor.get() and not self.syrup.get() and not any(v.get() for v in self.toppings.values()):
            return "🍦 Customize your sundae!"

        parts = []
        if self.flavor.get():
            parts.append(self.flavor.get())
        if self.syrup.get():
            parts.append(f"with {self.syrup.get()} syrup")
        chosen_toppings = [t for t, v in self.toppings.items() if v.get()]
        toppings_text = ", ".join(chosen_toppings) if chosen_toppings else "No toppings"
        return f"🍨 Sundae: {' '.join(parts)}\nToppings: {toppings_text}"

    def update_order(self):
        self.display.config(text=self.make_order_string())

    def clear_order(self):
        if messagebox.askyesno("Clear Order", "Clear the current sundae?"):
            self.flavor.set("")
            self.syrup.set("")
            for var in self.toppings.values():
                var.set(False)
            self.display.config(text="🍦 Customize your sundae!")

    def quit_app(self):
        if messagebox.askokcancel("Quit", "Quit the application?"):
            self.destroy()

    def save_order(self):
        order_text = self.make_order_string()
        if order_text == "🍦 Customize your sundae!":
            messagebox.showinfo("Nothing to save", "No sundae selected yet!")
            return
        path = filedialog.asksaveasfilename(
            title="Save Sundae",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(order_text + "\n")
                messagebox.showinfo("Saved", f"Order saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

if __name__ == "__main__":
    app = SundaeApp()
    app.mainloop()