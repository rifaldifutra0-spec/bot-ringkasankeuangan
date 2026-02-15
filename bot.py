import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from telegram.ext import ApplicationBuilder
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
FILE = "data_keuangan.json"

# =====================
# Helper
# =====================

def format_rupiah(angka):
    return "Rp{:,.0f}".format(angka).replace(",", ".")

def load_data():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# =====================
# Commands
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 BOT KEUANGAN PRIBADI AKTIF\n\n"
        "Perintah:\n"
        "/masuk jumlah keterangan\n"
        "/keluar jumlah keterangan\n"
        "/saldo\n"
        "/laporan_hari\n"
        "/grafik"
    )

async def masuk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    try:
        jumlah = int(context.args[0])
        ket = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Format salah!\nContoh:\n/masuk 50000 Gaji")
        return

    data = load_data()

    if user_id not in data:
        data[user_id] = []

    data[user_id].append({
        "tipe": "masuk",
        "jumlah": jumlah,
        "ket": ket,
        "tanggal": datetime.now().strftime("%Y-%m-%d")
    })

    save_data(data)
    await update.message.reply_text(f"✅ Pemasukan {format_rupiah(jumlah)} dicatat")

async def keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    try:
        jumlah = int(context.args[0])
        ket = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Format salah!\nContoh:\n/keluar 20000 Jajan")
        return

    data = load_data()

    if user_id not in data:
        data[user_id] = []

    data[user_id].append({
        "tipe": "keluar",
        "jumlah": jumlah,
        "ket": ket,
        "tanggal": datetime.now().strftime("%Y-%m-%d")
    })

    save_data(data)
    await update.message.reply_text(f"❌ Pengeluaran {format_rupiah(jumlah)} dicatat")

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    total = 0

    if user_id in data:
        for item in data[user_id]:
            if item["tipe"] == "masuk":
                total += item["jumlah"]
            else:
                total -= item["jumlah"]

    await update.message.reply_text(f"💰 Saldo kamu: {format_rupiah(total)}")

async def laporan_hari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    data = load_data()

    if user_id not in data:
        await update.message.reply_text("Belum ada transaksi")
        return

    teks = f"📅 Laporan Hari Ini ({today})\n\n"
    total = 0

    for item in data[user_id]:
        if item["tanggal"] == today:
            teks += f"{item['tipe']} - {format_rupiah(item['jumlah'])} - {item['ket']}\n"
            if item["tipe"] == "masuk":
                total += item["jumlah"]
            else:
                total -= item["jumlah"]

    teks += f"\nSaldo Hari Ini: {format_rupiah(total)}"
    await update.message.reply_text(teks)

async def grafik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        await update.message.reply_text("Belum ada data")
        return

    df = pd.DataFrame(data[user_id])
    df["jumlah"] = df["jumlah"].astype(int)

    masuk = df[df["tipe"] == "masuk"]["jumlah"].sum()
    keluar = df[df["tipe"] == "keluar"]["jumlah"].sum()

    plt.figure()
    plt.bar(["Pemasukan", "Pengeluaran"], [masuk, keluar])
    plt.title("Grafik Keuangan")
    plt.savefig("grafik.png")
    plt.close()

    await update.message.reply_photo(photo=open("grafik.png", "rb"))

# =====================
# Main
# =====================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("masuk", masuk))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("saldo", saldo))
app.add_handler(CommandHandler("laporan_hari", laporan_hari))
app.add_handler(CommandHandler("grafik", grafik))

app.run_polling()
