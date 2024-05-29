import tkinter as tk
from tkinter import messagebox, StringVar, IntVar, simpledialog
from tkinter import ttk
import pygame

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
            self.custom_messagebox("Selamat Datang", f"Selamat Datang, {user.email}!")
            self.display_gun_list(user)
        else:
            self.custom_messagebox("Error", "User tidak ditemukan.", "error")

    def display_gun_list(self, user: User):
        gun_list_str = "Persediaan:\n"
        for gun in user.gun_list:
            gun_list_str += f"- {gun.name}: {gun.stock}\n"
        self.custom_messagebox("Persediaan", gun_list_str)

    def display_weapons_stock(self):
        if not self.weapons:
            self.custom_messagebox("Stok Senjata", "Senjata Tidak Tersedia.")
        else:
            stock_str = "Stok Senjata:\n"
            for weapon in self.weapons:
                stock_str += f"- {weapon.name}: {weapon.stock}\n"
            self.custom_messagebox("Stok Senjata", stock_str)

    def get_stock_by_name(self, weapon_name: str) -> int:
        for weapon in self.weapons:
            if weapon.name.lower() == weapon_name.lower():
                return weapon.stock
        return None

    def update_weapon_stock(self, weapon_name: str, quantity: int):
        weapon = next((weapon for weapon in self.weapons if weapon.name.lower() == weapon_name.lower()), None)
        if weapon is not None:
            weapon.stock += quantity

    def custom_messagebox(self, title: str, message: str, type: str = "info"):
        root = tk.Tk()
        root.withdraw()
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="green", background="black", font=("Helvetica", 10))
        if type == "info":
            messagebox.showinfo(title, message)
        elif type == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
        root.destroy()

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
        weapon_name = tk.simpledialog.askstring(prompt, "Masukkan nama senjata:")
        if weapon_name is not None:
            weapon_stock = tk.simpledialog.askinteger(prompt, f"Masukkan jumlah stok {weapon_name}:")
            if weapon_stock is not None:
                weapon_price = tk.simpledialog.askinteger(prompt, f"Masukkan harga {weapon_name}:")
                if weapon_price is not None:
                    return weapon_name, weapon_stock, weapon_price
        return None, None, None

    def add_weapon(self):
        weapon_info = self._get_weapon_info("Tambah Senjata")
        if weapon_info:
            self.firearms_storage_user.weapons.append(Weapon(*weapon_info))

    def delete_weapon(self):
        weapon_name = tk.simpledialog.askstring("Hapus Senjata", "Masukkan nama senjata yang dihapus:")
        if weapon_name is not None:
            weapon = next((weapon for weapon in self.firearms_storage_user.weapons if weapon.name.lower() == weapon_name.lower()), None)
            if weapon is not None:
                self.firearms_storage_user.weapons.remove(weapon)

    def update_weapon_stock(self):
        weapon_name = tk.simpledialog.askstring("Perbarui Stok Senjata", "Masukkan nama senjata untuk diperbarui:")
        if weapon_name is not None:
            update_quantity = tk.simpledialog.askinteger("Perbarui Stok Senjata", f"Masukkan Jumlah untuk ditambah atau dikurang dari {weapon_name} (contoh: -10 atau 50):")
            if update_quantity is not None:
                self.firearms_storage_user.update_weapon_stock(weapon_name, update_quantity)

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

        weapon_label = tk.Label(frame, text=f"{weapon.name} (Stok: {weapon.stock}, Harga: {weapon.price})", fg='green', bg='black', font=("Helvetica", 10))
        weapon_label.pack(side=tk.LEFT, padx=5)

        quantity_var = IntVar()
        self.weapon_quantities[weapon.name] = quantity_var
        quantity_entry = tk.Entry(frame, textvariable=quantity_var, width=5, font=("Helvetica", 10), fg='green', bg='black')
        quantity_entry.pack(side=tk.RIGHT, padx=5)

    def book(self):
        order_details = "Nota:\n"
        total_cost = 0
        for weapon_name, quantity_var in self.weapon_quantities.items():
            quantity = quantity_var.get()
            if quantity > 0:
                weapon = next((w for w in self.firearms_storage_user.weapons if w.name == weapon_name), None)
                if weapon and weapon.stock >= quantity:
                    weapon.stock -= quantity
                    order_details += f"{weapon.name}: {quantity}\n"
                    total_cost += quantity * weapon.price
                else:
                    self.custom_messagebox("Error", f"Stok tidak cukup untuk {weapon_name}.", "error")
                    return
        order_details += f"\nTotal Biaya: {total_cost} IDR"
        order_details += "\nHubungi nomor telepon berikut untuk konfirmasi: 081234567890"

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

    def custom_messagebox(self, title: str, message: str, type: str = "info"):
        root = tk.Tk()
        root.withdraw()
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="green", background="black", font=("Helvetica", 10))
        if type == "info":
            messagebox.showinfo(title, message)
        elif type == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
        root.destroy()

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

        pygame.init()
        pygame.mixer.music.load("pump up kicks.mp3")
        pygame.mixer.music.play(-1)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
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
            self.custom_messagebox("Error", "Email atau password salah, silakan coba lagi.", "error")

    def validate_login(self, email: str, password: str) -> User:
        for user in self.user_data:
            if user["email"] == email and user["password"] == password:
                return User(user["email"], user["password"], user["role"], [weapon for weapon in self.weapons if user["email"] in weapon.name])
        return None

    def create_user_objects(self) -> dict:
        user_objects = {}
        for user in self.user_data:
            user_objects[user["email"]] = User(user["email"], user["password"], user["role"], [weapon for weapon in self.weapons if user["email"] in weapon.name])
        return user_objects

    def custom_messagebox(self, title: str, message: str, type: str = "info"):
        root = tk.Tk()
        root.withdraw()
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="green", background="black", font=("Helvetica", 10))
        if type == "info":
            messagebox.showinfo(title, message)
        elif type == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
        root.destroy()

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
