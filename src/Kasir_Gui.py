import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import os

# ================== KONFIG ==================
TOKO = "POJOK UMAH"
FILE_PRODUK = "produk.txt"
ADMIN_PASSWORD = "admin123"

# ================== DATA ==================
def load_produk():
    data = []
    if not os.path.exists(FILE_PRODUK):
        return data

    with open(FILE_PRODUK, "r") as f:
        for line in f:
            if line.strip():
                x = line.strip().split("|")
                while len(x) < 5:
                    x.append("0")
                k, n, h, s, d = x
                data.append({
                    "kode": k,
                    "nama": n,
                    "harga": int(h),
                    "stok": int(s),
                    "diskon": int(d)
                })
    return data

def save_produk(data):
    with open(FILE_PRODUK, "w") as f:
        for p in data:
            f.write(f"{p['kode']}|{p['nama']}|{p['harga']}|{p['stok']}|{p['diskon']}\n")

def harga_final(p):
    return p["harga"] - (p["harga"] * p["diskon"] // 100)

# ================== GUI ==================
class App:
    def __init__(self, root):
        self.root = root
        root.title("Program Kasir - POJOK UMAH")
        root.geometry("950x600")
        root.resizable(False, False)

        self.produk = load_produk()
        self.keranjang = []

        tk.Label(root, text=TOKO, font=("Arial", 22, "bold")).pack(pady=5)

        top = tk.Frame(root)
        top.pack()
        tk.Label(top, text="Nama Kasir:").pack(side=tk.LEFT)
        self.entry_kasir = tk.Entry(top, width=25)
        self.entry_kasir.pack(side=tk.LEFT)

        tk.Button(top, text="Menu Admin", command=self.menu_admin).pack(side=tk.LEFT, padx=10)

        main = tk.Frame(root)
        main.pack(pady=10)

        self.listbox = tk.Listbox(main, width=55, height=15)
        self.listbox.pack(side=tk.LEFT, padx=10)
        self.refresh_produk()

        right = tk.Frame(main)
        right.pack(side=tk.LEFT)

        tk.Label(right, text="Jumlah").pack()
        self.qty = tk.Entry(right)
        self.qty.pack()

        tk.Button(right, text="Tambah ke Keranjang", width=22,
                  command=self.tambah).pack(pady=5)
        tk.Button(right, text="Proses Pembayaran", width=22,
                  command=self.bayar).pack(pady=20)

        self.struk = tk.Text(root, height=15)
        self.struk.pack(fill=tk.X, padx=10)

    # ================= KASIR =================
    def refresh_produk(self):
        self.listbox.delete(0, tk.END)
        for p in self.produk:
            self.listbox.insert(
                tk.END,
                f"[{p['kode']}] {p['nama']} | Rp{harga_final(p)} | Stok {p['stok']} | Diskon {p['diskon']}%"
            )

    def tambah(self):
        if not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        p = self.produk[idx]

        try:
            j = int(self.qty.get())
        except:
            return

        if j <= 0 or j > p["stok"]:
            messagebox.showerror("Error", "Jumlah tidak valid")
            return

        total = harga_final(p) * j
        self.keranjang.append((p["nama"], j, total))
        p["stok"] -= j
        save_produk(self.produk)

        self.refresh_produk()
        self.qty.delete(0, tk.END)

    def bayar(self):
        if not self.keranjang:
            return

        kasir = self.entry_kasir.get()
        if not kasir:
            messagebox.showerror("Error", "Nama kasir kosong")
            return

        metode = messagebox.askquestion(
            "Pembayaran",
            "YES = Cash\nNO = Non-Cash (QRIS)"
        )

        total = sum(i[2] for i in self.keranjang)

        if metode == "yes":
            while True:
                bayar = simpledialog.askinteger("Cash", f"Total Rp{total}\nUang dibayar:")
                if bayar is None:
                    return
                if bayar >= total:
                    break
                messagebox.showwarning("Kurang", f"Kurang Rp{total - bayar}")
            metode_text = "Cash"
        else:
            bayar = total
            metode_text = "Non-Cash (QRIS)"

        now = datetime.now()

        self.struk.delete("1.0", tk.END)
        self.struk.insert(tk.END, f"{TOKO}\n")
        self.struk.insert(tk.END, now.strftime("%A, %d-%m-%Y %H:%M:%S\n"))
        self.struk.insert(tk.END, f"Kasir  : {kasir}\n")
        self.struk.insert(tk.END, f"Metode : {metode_text}\n")
        self.struk.insert(tk.END, "-"*35 + "\n")

        for i in self.keranjang:
            self.struk.insert(tk.END, f"{i[0]} x{i[1]} = Rp{i[2]}\n")

        self.struk.insert(tk.END, "-"*35 + "\n")
        self.struk.insert(tk.END, f"TOTAL : Rp{total}\n")
        self.struk.insert(tk.END, f"BAYAR : Rp{bayar}\n")
        self.struk.insert(tk.END, f"KEMBALI : Rp{bayar-total}\n")
        self.struk.insert(tk.END, "TERIMA KASIH\n")

        self.keranjang.clear()

    # ================= ADMIN =================
    def menu_admin(self):
        pw = simpledialog.askstring("Admin", "Password:", show="*")
        if pw != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Password salah")
            return

        win = tk.Toplevel(self.root)
        win.title("Menu Admin")
        win.geometry("500x400")

        lb = tk.Listbox(win, width=60)
        lb.pack(pady=10)

        def refresh():
            lb.delete(0, tk.END)
            for p in self.produk:
                lb.insert(tk.END, f"{p['kode']} | {p['nama']} | Rp{p['harga']} | Stok {p['stok']} | Diskon {p['diskon']}%")

        def tambah():
            k = simpledialog.askstring("Kode", "Kode produk:")
            n = simpledialog.askstring("Nama", "Nama produk:")
            h = simpledialog.askinteger("Harga", "Harga:")
            s = simpledialog.askinteger("Stok", "Stok:")
            d = simpledialog.askinteger("Diskon", "Diskon %:", initialvalue=0)
            if None in (k, n, h, s):
                return
            self.produk.append({"kode":k,"nama":n,"harga":h,"stok":s,"diskon":d})
            save_produk(self.produk)
            refresh()
            self.refresh_produk()

        def hapus():
            if not lb.curselection(): return
            self.produk.pop(lb.curselection()[0])
            save_produk(self.produk)
            refresh()
            self.refresh_produk()

        tk.Button(win, text="Tambah Produk", command=tambah).pack()
        tk.Button(win, text="Hapus Produk", command=hapus).pack(pady=5)

        refresh()

# ================= RUN =================
root = tk.Tk()
App(root)
root.mainloop()
