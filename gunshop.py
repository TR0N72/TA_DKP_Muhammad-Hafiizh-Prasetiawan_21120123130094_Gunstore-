import tkinter as tk
from tkinter import messagebox, StringVar, IntVar, simpledialog
from tkinter import ttk
import pygame
import os


# --- Shared Utility ---
def custom_messagebox(title: str, message: str, msg_type: str = "info"):
    """Shared messagebox utility. Uses the existing Tk root instead of creating a new one."""
    if msg_type == "error":
        messagebox.showerror(title, message)
    else:
        messagebox.showinfo(title, message)


class Weapon:
    def __init__(self, name: str, stock: int, price: int):
        self.name = name
        self.stock = stock
        self.price = price


class User:
    def __init__(self, email: str, password: str, role: str, gun_list: list = None):
        self.email = email
        self.password = password
        self.role = role
        self.gun_list = gun_list if gun_list is not None else []


class FirearmsStorageUser:
    def __init__(self, user_objects: dict, weapons: list):
        self.user_objects = user_objects
        self.weapons = weapons

    def display_info(self, email: str):
        user = self.user_objects.get(email)
        if user:
            custom_messagebox("Selamat Datang", f"Selamat Datang, {user.email}!")
            self.display_gun_list(user)
        else:
            custom_messagebox("Error", "User tidak ditemukan.", "error")

    def display_gun_list(self, user: User):
        gun_list_str = "Persediaan:\n"
        for gun in user.gun_list:
            gun_list_str += f"- {gun.name}: {gun.stock}\n"
        if not user.gun_list:
            gun_list_str += "(Kosong)"
        custom_messagebox("Persediaan", gun_list_str)

    def display_weapons_stock(self):
        if not self.weapons:
            custom_messagebox("Stok Senjata", "Senjata Tidak Tersedia.")
        else:
            stock_str = "Stok Senjata:\n"
            for weapon in self.weapons:
                stock_str += f"- {weapon.name}: {weapon.stock} (Harga: {weapon.price:,} IDR)\n"
            custom_messagebox("Stok Senjata", stock_str)

    def get_stock_by_name(self, weapon_name: str) -> int:
        for weapon in self.weapons:
            if weapon.name.lower() == weapon_name.lower():
                return weapon.stock
        return None

    def update_weapon_stock(self, weapon_name: str, quantity: int):
        weapon = next((weapon for weapon in self.weapons if weapon.name.lower() == weapon_name.lower()), None)
        if weapon is not None:
            new_stock = weapon.stock + quantity
            if new_stock < 0:
                custom_messagebox("Error", f"Stok {weapon.name} tidak bisa kurang dari 0.", "error")
                return False
            weapon.stock = new_stock
            return True
        else:
            custom_messagebox("Error", f"Senjata '{weapon_name}' tidak ditemukan.", "error")
            return False


class AdminGUI(tk.Toplevel):
    def __init__(self, master, firearms_storage_user: FirearmsStorageUser):
        super().__init__(master)
        self.firearms_storage_user = firearms_storage_user
        self.title("Admin Menu")
        self.geometry("400x400")
        self.configure(bg='black')

        self.add_weapon_button = tk.Button(self, text="Tambah Senjata", command=self.add_weapon, fg='green', bg='black', font=("Helvetica", 10))
        self.add_weapon_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        self.delete_weapon_button = tk.Button(self, text="Hapus Senjata", command=self.delete_weapon, fg='green', bg='black', font=("Helvetica", 10))
        self.delete_weapon_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        self.update_weapon_stock_button = tk.Button(self, text="Perbarui Stok Senjata", command=self.update_weapon_stock, fg='green', bg='black', font=("Helvetica", 10))
        self.update_weapon_stock_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.display_weapons_stock_button = tk.Button(self, text="Stok Senjata", command=self.display_weapons_stock, fg='green', bg='black', font=("Helvetica", 10))
        self.display_weapons_stock_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.exit_button = tk.Button(self, text="Keluar", command=self.exit_to_login, fg='green', bg='black', font=("Helvetica", 10))
        self.exit_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def _get_weapon_info(self, prompt: str) -> tuple:
        weapon_name = simpledialog.askstring(prompt, "Masukkan nama senjata:", parent=self)
        if weapon_name is None or weapon_name.strip() == "":
            return None, None, None
        weapon_name = weapon_name.strip()

        weapon_stock = simpledialog.askinteger(prompt, f"Masukkan jumlah stok {weapon_name}:", parent=self)
        if weapon_stock is None:
            return None, None, None
        if weapon_stock < 0:
            custom_messagebox("Error", "Stok tidak boleh negatif.", "error")
            return None, None, None

        weapon_price = simpledialog.askinteger(prompt, f"Masukkan harga {weapon_name}:", parent=self)
        if weapon_price is None:
            return None, None, None
        if weapon_price <= 0:
            custom_messagebox("Error", "Harga harus lebih dari 0.", "error")
            return None, None, None

        return weapon_name, weapon_stock, weapon_price

    def add_weapon(self):
        weapon_name, weapon_stock, weapon_price = self._get_weapon_info("Tambah Senjata")
        if weapon_name is not None:
            self.firearms_storage_user.weapons.append(Weapon(weapon_name, weapon_stock, weapon_price))
            custom_messagebox("Sukses", f"Senjata '{weapon_name}' berhasil ditambahkan.")

    def delete_weapon(self):
        weapon_name = simpledialog.askstring("Hapus Senjata", "Masukkan nama senjata yang dihapus:", parent=self)
        if weapon_name is not None:
            weapon = next((weapon for weapon in self.firearms_storage_user.weapons if weapon.name.lower() == weapon_name.strip().lower()), None)
            if weapon is not None:
                self.firearms_storage_user.weapons.remove(weapon)
                custom_messagebox("Sukses", f"Senjata '{weapon.name}' berhasil dihapus.")
            else:
                custom_messagebox("Error", f"Senjata '{weapon_name}' tidak ditemukan.", "error")

    def update_weapon_stock(self):
        weapon_name = simpledialog.askstring("Perbarui Stok Senjata", "Masukkan nama senjata untuk diperbarui:", parent=self)
        if weapon_name is not None:
            update_quantity = simpledialog.askinteger("Perbarui Stok Senjata", f"Masukkan Jumlah untuk ditambah atau dikurang dari {weapon_name} (contoh: -10 atau 50):", parent=self)
            if update_quantity is not None:
                if self.firearms_storage_user.update_weapon_stock(weapon_name, update_quantity):
                    custom_messagebox("Sukses", f"Stok '{weapon_name}' berhasil diperbarui.")

    def display_weapons_stock(self):
        self.firearms_storage_user.display_weapons_stock()

    def exit_to_login(self):
        self.destroy()
        self.master.deiconify()


class MarketGUI(tk.Toplevel):
    def __init__(self, master, user: User, firearms_storage_user: FirearmsStorageUser):
        super().__init__(master)
        self.user = user
        self.firearms_storage_user = firearms_storage_user
        self.title("LambGun store")
        self.geometry("800x700")
        self.configure(bg='black')

        self.weapon_quantities = {}
        self.weapon_labels = {}

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self, text="Lambs of Guns Store", fg='green', bg='black', font=("Helvetica", 20))
        title_label.pack(pady=10)

        instruction_label = tk.Label(self, text="Pilih Senjata Yang Ingin Anda Beli dan Masukkan Jumlah:", fg='green', bg='black', font=("Helvetica", 12))
        instruction_label.pack(pady=10)

        self.weapon_frame = tk.Frame(self, bg='black')
        self.weapon_frame.pack(pady=10)

        for weapon in self.firearms_storage_user.weapons:
            self.create_weapon_entry(weapon)

        self.order_button = tk.Button(self, text="Pesan", command=self.book, fg='green', bg='black', font=("Helvetica", 12))
        self.order_button.pack(pady=10)

        self.exit_button = tk.Button(self, text="Keluar", command=self.exit_to_login, fg='green', bg='black', font=("Helvetica", 12))
        self.exit_button.pack(pady=10)

    def create_weapon_entry(self, weapon):
        frame = tk.Frame(self.weapon_frame, bg='black')
        frame.pack(fill=tk.X, pady=5)

        weapon_label = tk.Label(frame, text=f"{weapon.name} (Stok: {weapon.stock}, Harga: {weapon.price:,} IDR)", fg='green', bg='black', font=("Helvetica", 10))
        weapon_label.pack(side=tk.LEFT, padx=5)
        self.weapon_labels[weapon.name] = weapon_label

        quantity_var = IntVar()
        self.weapon_quantities[weapon.name] = quantity_var
        quantity_entry = tk.Entry(frame, textvariable=quantity_var, width=5, font=("Helvetica", 10), fg='green', bg='black')
        quantity_entry.pack(side=tk.RIGHT, padx=5)

    def refresh_weapon_labels(self):
        """Update all weapon labels to reflect current stock values."""
        for weapon in self.firearms_storage_user.weapons:
            if weapon.name in self.weapon_labels:
                self.weapon_labels[weapon.name].config(
                    text=f"{weapon.name} (Stok: {weapon.stock}, Harga: {weapon.price:,} IDR)"
                )

    def book(self):
        order_details = "Nota:\n"
        total_cost = 0
        has_items = False

        for weapon_name, quantity_var in self.weapon_quantities.items():
            quantity = quantity_var.get()
            if quantity < 0:
                custom_messagebox("Error", f"Jumlah untuk {weapon_name} tidak boleh negatif.", "error")
                return
            if quantity > 0:
                has_items = True
                weapon = next((w for w in self.firearms_storage_user.weapons if w.name == weapon_name), None)
                if weapon and weapon.stock >= quantity:
                    weapon.stock -= quantity
                    order_details += f"{weapon.name}: {quantity}\n"
                    total_cost += quantity * weapon.price
                else:
                    custom_messagebox("Error", f"Stok tidak cukup untuk {weapon_name}.", "error")
                    return

        if not has_items:
            custom_messagebox("Error", "Anda belum memilih senjata apapun.", "error")
            return

        order_details += f"\nTotal Biaya: {total_cost:,} IDR"
        order_details += "\nHubungi nomor telepon berikut untuk konfirmasi: 081234567890"

        # Refresh labels to show updated stock
        self.refresh_weapon_labels()

        # Reset quantity fields
        for quantity_var in self.weapon_quantities.values():
            quantity_var.set(0)

        receipt_window = tk.Toplevel(self)
        receipt_window.title("Nota")
        receipt_window.geometry("400x400")
        receipt_window.configure(bg='black')

        receipt_label = tk.Label(receipt_window, text=order_details, fg='green', bg='black', font=("Helvetica", 10))
        receipt_label.pack(pady=10)

        ok_button = tk.Button(receipt_window, text="OK", command=receipt_window.destroy, fg='green', bg='black', font=("Helvetica", 10))
        ok_button.pack(pady=10)

        self.center_window(receipt_window)

    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        width = 400
        height = 300
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    def exit_to_login(self):
        self.destroy()
        self.master.deiconify()


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stok senjata")
        self.geometry("400x300")
        self.configure(bg='black')

        self.email_label = tk.Label(self, text="Email:", fg='green', bg='black', font=("Helvetica", 10))
        self.email_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        self.email_entry = tk.Entry(self, width=30, fg='green', bg='black', font=("Helvetica", 10))
        self.email_entry.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        self.password_label = tk.Label(self, text="Password:", fg='green', bg='black', font=("Helvetica", 10))
        self.password_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.password_entry = tk.Entry(self, width=30, show="*", fg='green', bg='black', font=("Helvetica", 10))
        self.password_entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.login_button = tk.Button(self, text="Login", command=self.login, fg='green', bg='black', font=("Helvetica", 10))
        self.login_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        self.user_data = [
            {"email": "baihaqi@test.com", "password": "1234", "role": "admin"},
            {"email": "faiz@test.com", "password": "5678", "role": "customer"},
            {"email": "hafiizh@test.com", "password": "9012", "role": "customer"},
            {"email": "zulfa@test.com", "password": "3456", "role": "customer"}
        ]

        self.weapons = [
            Weapon("AK-47", 100, 450000000),
            Weapon("Glock-18", 250, 300000000),
            Weapon("Dragunov SVD", 50, 260000000),
            Weapon("PINDAD SS-1", 80, 120000000),
            Weapon("PzB 38", 10, 500000000),
            Weapon("Remington 870", 45, 245000000),
            Weapon("M4A1", 84, 760000000),
            Weapon("M249 SAW", 20, 1100000000),
            Weapon("Hekler & Koch MP5", 175, 540000000),
            Weapon("SIG Sauer P226", 90, 475000000),
            Weapon("Barret M82A1", 130, 760000000),
            Weapon("HK USP", 300, 245000000),
            Weapon("Desert Eagle.50 AE", 20, 500000000),
            Weapon("Ruger 10/22", 99, 120000000),
            Weapon("FN Scar 17S", 200, 260000000)
        ]

        # Use absolute path relative to script location for music file
        try:
            pygame.init()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            music_path = os.path.join(script_dir, "pump up kicks.mp3")
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
            else:
                print(f"Warning: Music file not found at {music_path}")
        except Exception as e:
            print(f"Warning: Could not initialize music: {e}")

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        if not email or not password:
            custom_messagebox("Error", "Email dan password harus diisi.", "error")
            return
        user = self.validate_login(email, password)
        if user:
            self.firearms_storage_user = FirearmsStorageUser(self.create_user_objects(), self.weapons)
            if user.role == "admin":
                self.withdraw()
                AdminGUI(self, self.firearms_storage_user)
            else:
                self.withdraw()
                MarketGUI(self, user, self.firearms_storage_user)
        else:
            custom_messagebox("Error", "Email atau password salah, silakan coba lagi.", "error")

    def validate_login(self, email: str, password: str) -> User:
        for user in self.user_data:
            if user["email"] == email and user["password"] == password:
                return User(user["email"], user["password"], user["role"], list(self.weapons))
        return None

    def create_user_objects(self) -> dict:
        user_objects = {}
        for user in self.user_data:
            user_objects[user["email"]] = User(user["email"], user["password"], user["role"], list(self.weapons))
        return user_objects


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
