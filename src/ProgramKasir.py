import os
from datetime import datetime

PASSWORD = "kasir123"
NAMA_TOKO = "POJOK UMAH"

PRODUK_FILE = "produk.txt"
PENJUALAN_FILE = "penjualan.txt"

def init_file():
    for f in [PRODUK_FILE, PENJUALAN_FILE]:
        if not os.path.exists(f):
            open(f, "w").close()


def load_produk():
    produk = {}
    with open(PRODUK_FILE, "r") as f:
        for line in f:
            if line.strip():
                data = line.strip().split("|")

                if len(data) == 4:
                    k, n, h, s = data
                    d = 0
                else:
                    k, n, h, s, d = data

                produk[k] = {
                    "nama": n,
                    "harga": int(h),
                    "stok": int(s),
                    "diskon": int(d)
                }
    return produk


def save_produk(produk):
    with open(PRODUK_FILE, "w") as f:
        for k, d in produk.items():
            f.write(f"{k}|{d['nama']}|{d['harga']}|{d['stok']}|{d['diskon']}\n")


def harga_final(harga, diskon):
    return harga - (harga * diskon // 100)


def generate_kode_transaksi():
    return "TRX-" + datetime.now().strftime("%Y%m%d-%H%M%S")

def tampil_produk_customer():
    produk = load_produk()
    daftar = list(produk.items())

    print("\n========= DAFTAR PRODUK =========")
    for i, (k, d) in enumerate(daftar, 1):
        status = "HABIS" if d["stok"] == 0 else f"Stok: {d['stok']}"
        print(f"{i}. [{k}] {d['nama']}")
        print(f"   Harga : Rp{d['harga']}")
        print(f"   Diskon: {d['diskon']}%")
        print(f"   Final : Rp{harga_final(d['harga'], d['diskon'])}")
        print(f"   {status}")
        print("-" * 35)
    return daftar


def tampil_produk_admin(produk=None):
    if produk is None:
        produk = load_produk()

    print("\nKODE | NAMA | HARGA | STOK | DISKON")
    print("-" * 60)
    for k, d in produk.items():
        print(f"{k} | {d['nama']} | Rp{d['harga']} | {d['stok']} | {d['diskon']}%")
    print("-" * 60)

def beli_produk():
    produk = load_produk()
    if not produk:
        print("Produk kosong.\n")
        return

    nama_kasir = input("Nama Kasir: ")

    keranjang = []
    total = 0

    while True:
        daftar = tampil_produk_customer()
        pilih = input("Pilih nomor produk (0 selesai): ")

        if pilih == "0":
            break

        if not pilih.isdigit() or int(pilih) < 1 or int(pilih) > len(daftar):
            print("Nomor tidak valid!\n")
            continue

        kode, d = daftar[int(pilih) - 1]

        if d["stok"] == 0:
            print("Produk HABIS!\n")
            continue

        qty = int(input("Jumlah beli: "))
        if qty <= 0 or qty > d["stok"]:
            print("Jumlah tidak valid!\n")
            continue

        harga = harga_final(d["harga"], d["diskon"])
        subtotal = harga * qty

        produk[kode]["stok"] -= qty
        keranjang.append((kode, d["nama"], harga, qty, subtotal))
        total += subtotal

    if not keranjang:
        print("Tidak ada pembelian.\n")
        return

    kode_trx = generate_kode_transaksi()

    print("\n========= STRUK BELANJA =========")
    for i in keranjang:
        print(f"[{i[0]}] {i[1]} x{i[3]} = Rp{i[4]}")
    print("-" * 35)
    print(f"TOTAL : Rp{total}")

    print("\nMetode Pembayaran")
    print("1. Cash")
    print("2. Non-Cash (QR / Transfer)")
    metode = input("Pilih: ")

    if metode == "1":
        while True:
            bayar = int(input("Uang dibayar: "))
            if bayar >= total:
                break
            print(f"Uang kurang Rp{total - bayar}")
    else:
        bayar = total
        print("Pembayaran non-cash berhasil.")

    kembalian = bayar - total
    now = datetime.now()

    hari = now.strftime("%A")
    tanggal = now.strftime("%d-%m-%Y")
    jam = now.strftime("%H:%M:%S")

    with open(PENJUALAN_FILE, "a") as f:
        f.write(f"{tanggal} {jam}|{kode_trx}|{total}|{nama_kasir}\n")

    save_produk(produk)

    print("\n================================")
    print(f"        {NAMA_TOKO}")
    print("================================")
    print(f"Hari    : {hari}")
    print(f"Tanggal : {tanggal}")
    print(f"Jam     : {jam}")
    print(f"Kasir   : {nama_kasir}")
    print(f"No TRX  : {kode_trx}")
    print("--------------------------------")

    for i in keranjang:
        print(f"{i[1]} x{i[3]}  Rp{i[4]}")

    print("--------------------------------")
    print(f"TOTAL     : Rp{total}")
    print(f"BAYAR     : Rp{bayar}")
    print(f"KEMBALIAN : Rp{kembalian}")
    print("================================")
    print("   TERIMA KASIH TELAH BELANJA")
    print("================================\n")

def tambah_produk():
    p = load_produk()
    k = input("Kode produk : ")
    p[k] = {
        "nama": input("Nama  : "),
        "harga": int(input("Harga : ")),
        "stok": int(input("Stok  : ")),
        "diskon": int(input("Diskon (%) : "))
    }
    save_produk(p)


def edit_produk():
    p = load_produk()
    tampil_produk_admin(p)
    k = input("Kode produk: ")

    if k in p:
        p[k]["nama"] = input("Nama baru : ")
        p[k]["harga"] = int(input("Harga baru: "))
        p[k]["diskon"] = int(input("Diskon (%) : "))
        save_produk(p)
        print("Produk diupdate.\n")


def tambah_stok():
    p = load_produk()
    tampil_produk_admin(p)
    k = input("Kode produk: ")

    if k in p:
        p[k]["stok"] += int(input("Tambah stok: "))
        save_produk(p)
        print("Stok ditambah.\n")


def hapus_produk():
    p = load_produk()
    tampil_produk_admin(p)
    k = input("Kode produk: ")

    if k in p:
        if input("Yakin hapus produk? (y/n): ").lower() == "y":
            del p[k]
            save_produk(p)
            print("Produk dihapus.\n")
        else:
            print("Dibatalkan.\n")


def cari_produk():
    p = load_produk()
    keyword = input("Cari (kode/nama): ").lower()

    hasil = {
        k: d for k, d in p.items()
        if keyword in k.lower() or keyword in d["nama"].lower()
    }

    if hasil:
        tampil_produk_admin(hasil)
    else:
        print("Produk tidak ditemukan.\n")


def sorting_produk():
    p = load_produk()
    print("1. Nama")
    print("2. Harga")
    print("3. Stok")
    print("4. Stok paling sedikit")
    print("5. Diskon terbesar")

    c = input("Sorting: ")

    key_map = {
        "1": lambda x: x[1]["nama"],
        "2": lambda x: x[1]["harga"],
        "3": lambda x: x[1]["stok"],
        "4": lambda x: x[1]["stok"],
        "5": lambda x: -x[1]["diskon"]
    }

    if c in key_map:
        tampil_produk_admin(dict(sorted(p.items(), key=key_map[c])))


def menu_admin():
    if input("Password admin: ") != PASSWORD:
        print("Password salah!\n")
        return

    while True:
        print("\n=== MENU ADMIN ===")
        print("1. Tambah Produk")
        print("2. Edit Produk")
        print("3. Tambah Stok")
        print("4. Hapus Produk")
        print("5. Sorting Produk")
        print("6. Cari Produk")
        print("7. Lihat Produk")
        print("0. Kembali")

        p = input("Pilih: ")

        if p == "1":
            tambah_produk()
        elif p == "2":
            edit_produk()
        elif p == "3":
            tambah_stok()
        elif p == "4":
            hapus_produk()
        elif p == "5":
            sorting_produk()
        elif p == "6":
            cari_produk()
        elif p == "7":
            tampil_produk_admin()
        elif p == "0":
            break

def menu():
    while True:
        print("\n=== PROGRAM KASIR ===")
        print("1. Beli Produk")
        print("2. Menu Admin")
        print("0. Keluar")

        p = input("Pilih: ")

        if p == "1":
            beli_produk()
        elif p == "2":
            menu_admin()
        elif p == "0":
            print("Program selesai.")
            break


init_file()
menu()
