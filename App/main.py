import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

class ModManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sims 4 Modpack Manager")
        self.geometry("900x600")
        self.minsize(700, 400)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.modpacks_dir = os.path.expanduser("~/Sims4Modpacks")
        self.theme = "System"
        self.color_theme_var = ctk.StringVar(value="blue")  # Ensure always exists

        self.create_toolbar()
        self.create_main_area()

    def create_toolbar(self):
        from PIL import Image, ImageTk
        toolbar = ctk.CTkFrame(self, height=50)
        toolbar.pack(side="top", fill="x")

        # Theme popover button
        icon_path = os.path.join(os.path.dirname(__file__), "assets/png/Placeholder.png")
        try:
            icon_img = Image.open(icon_path).resize((32, 32))
            self.theme_icon = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(32, 32))
        except Exception:
            self.theme_icon = None
        self.theme_popover = None
        theme_btn = ctk.CTkButton(toolbar, text="", image=self.theme_icon, width=40, height=40, command=self.toggle_theme_popover, fg_color="transparent", hover_color="#e0e0e0", border_width=0)
        theme_btn.pack(side="left", padx=(10, 2))

        # Modpacks folder selector
        ctk.CTkLabel(toolbar, text="Storage Folder:").pack(side="left", padx=(20, 2))
        self.folder_var = ctk.StringVar(value=self.modpacks_dir)
        folder_entry = ctk.CTkEntry(toolbar, textvariable=self.folder_var, width=250)
        folder_entry.pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Browse", command=self.browse_folder).pack(side="left", padx=5)

    def toggle_theme_popover(self):
        if self.theme_popover and self.theme_popover.winfo_exists():
            self.theme_popover.destroy()
            self.theme_popover = None
            return
        # Create popover window
        self.theme_popover = ctk.CTkToplevel(self)
        self.theme_popover.overrideredirect(True)
        self.theme_popover.lift()
        self.theme_popover.geometry(f"220x180+{self.winfo_x()+60}+{self.winfo_y()+60}")
        self.theme_popover.configure(fg_color=self._apply_appearance_mode(ctk.ThemeManager.theme['CTkFrame']['fg_color']))

        # Segmented control for appearance mode
        ctk.CTkLabel(self.theme_popover, text="Appearance Mode:").pack(pady=(10, 2))
        self.appearance_var = ctk.StringVar(value=ctk.get_appearance_mode())
        seg = ctk.CTkSegmentedButton(self.theme_popover, values=["Light", "Dark", "System"], variable=self.appearance_var, command=self.change_theme)
        seg.pack(pady=2)

        # Color theme buttons
        ctk.CTkLabel(self.theme_popover, text="Color Theme:").pack(pady=(10, 2))
        color_frame = ctk.CTkFrame(self.theme_popover, fg_color="transparent")
        color_frame.pack(pady=2)
        for color in ["blue", "green", "dark-blue"]:
            btn = ctk.CTkButton(color_frame, text=color.capitalize(), width=60, height=28, command=lambda c=color: self.change_color_theme_popover(c))
            btn.pack(side="left", padx=4)

        # Dismiss popover on focus out
        self.theme_popover.bind("<FocusOut>", lambda e: self.theme_popover.destroy())
        self.theme_popover.focus_set()

    def change_color_theme_popover(self, value):
        if hasattr(self, 'color_theme_var'):
            self.color_theme_var.set(value)
        self.change_color_theme(value)
        if self.theme_popover and self.theme_popover.winfo_exists():
            self.theme_popover.destroy()
            self.theme_popover = None

    def change_theme(self, value):
        ctk.set_appearance_mode(value)
        self.theme = value
        # If popover exists, update segmented control
        if hasattr(self, 'appearance_var'):
            self.appearance_var.set(value)

    def change_color_theme(self, value):
        ctk.set_default_color_theme(value)
        # Recreate all UI to apply color theme everywhere
        for widget in self.winfo_children():
            widget.destroy()
        self.create_toolbar()
        self.create_main_area()

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get(), title="Select Modpacks Storage Folder")
        if folder:
            self.folder_var.set(folder)
            self.modpacks_dir = folder

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_modpack_cards()

    def refresh_modpack_cards(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        modpacks = self.get_modpacks()
        row = 0
        col = 0
        for modpack in modpacks:
            card = self.create_modpack_card(self.main_frame, modpack)
            card.grid(row=row, column=col, padx=15, pady=15)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        # Add new modpack card
        add_card = self.create_add_modpack_card(self.main_frame)
        add_card.grid(row=row, column=col, padx=15, pady=15)

    def get_modpacks(self):
        if not os.path.exists(self.modpacks_dir):
            os.makedirs(self.modpacks_dir)
        return [d for d in os.listdir(self.modpacks_dir) if os.path.isdir(os.path.join(self.modpacks_dir, d))]

    def create_modpack_card(self, parent, modpack_name):
        frame = ctk.CTkFrame(parent, width=200, height=120)
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=modpack_name, font=("Arial", 16, "bold")).pack(pady=(20, 5))
        ctk.CTkButton(frame, text="Activate", command=lambda: self.activate_modpack(modpack_name)).pack(pady=2)
        ctk.CTkButton(frame, text="Rename", command=lambda: self.rename_modpack(modpack_name)).pack(pady=2)
        ctk.CTkButton(frame, text="Delete", fg_color="red", command=lambda: self.delete_modpack(modpack_name)).pack(pady=2)
        return frame

    def create_add_modpack_card(self, parent):
        frame = ctk.CTkFrame(parent, width=200, height=120, fg_color="#e0e0e0")
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text="+ Add Modpack", font=("Arial", 16, "bold"), text_color="#333").pack(expand=True)
        frame.bind("<Button-1>", lambda e: self.add_modpack())
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e: self.add_modpack())
        return frame

    def add_modpack(self):
        name = ctk.CTkInputDialog(text="Enter new modpack name:", title="Add Modpack").get_input()
        if name:
            path = os.path.join(self.modpacks_dir, name)
            if os.path.exists(path):
                messagebox.showerror("Error", "A modpack with this name already exists.")
            else:
                os.makedirs(path)
                self.refresh_modpack_cards()

    def rename_modpack(self, modpack_name):
        new_name = ctk.CTkInputDialog(text=f"Rename '{modpack_name}' to:", title="Rename Modpack").get_input()
        if new_name and new_name != modpack_name:
            old_path = os.path.join(self.modpacks_dir, modpack_name)
            new_path = os.path.join(self.modpacks_dir, new_name)
            if os.path.exists(new_path):
                messagebox.showerror("Error", "A modpack with this name already exists.")
            else:
                os.rename(old_path, new_path)
                self.refresh_modpack_cards()

    def delete_modpack(self, modpack_name):
        if messagebox.askyesno("Delete Modpack", f"Are you sure you want to delete '{modpack_name}'?"):
            path = os.path.join(self.modpacks_dir, modpack_name)
            try:
                import shutil
                shutil.rmtree(path)
                self.refresh_modpack_cards()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete modpack: {e}")

    def activate_modpack(self, modpack_name):
        # Placeholder for actual activation logic
        messagebox.showinfo("Activate", f"Activated modpack: {modpack_name}")

if __name__ == "__main__":
    app = ModManagerApp()
    app.mainloop()
