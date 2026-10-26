import telebot
from telebot import types
import json
import os
import random
import time

TOKEN = "8808030519:AAGbH8HnvoyYHrB-0QQCmJfpnyfsYcaH29Y"
ADMIN_ID = 8513725971
ADMIN_USERNAME = "@Lasmontero"

# URL GitHub Pages Mini Game
URL_MINIAPP_GAME = "https://faryandhiayeza-bit.github.io/Sadajiwa-game/"

bot = telebot.TeleBot(TOKEN)

DB_FILE = "database_user.json"
KATALOG_FILE = "katalog_motor.json"

# --- HELPER DATABASE ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_katalog():
    if not os.path.exists(KATALOG_FILE):
        return {}
    with open(KATALOG_FILE, "r") as f:
        return json.load(f)

# --- 1. MENU UTAMA, BUBBLECHAT & DAFTAR FITUR ---
@bot.message_handler(commands=['start'])
def sambutan(pesan):
    user_id = str(pesan.from_user.id)
    nama = pesan.from_user.first_name
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            "nama": nama,
            "koin": 1500,
            "total_topup": 0,
            "total_race": 0,
            "total_win": 0,
            "motor": {
                "nama_motor": "Vespa Paddock Edition",
                "mesin_lvl": 1,
                "speed": 115,
                "oli": 100
            }
        }
        save_data(data)
        status_user = "Pembalap Baru (Bonus Starter: 💰 1,500 Koin)"
    else:
        data[user_id].setdefault("total_topup", 0)
        data[user_id].setdefault("total_race", 0)
        data[user_id].setdefault("total_win", 0)
        save_data(data)
        status_user = "Pembalap Veteran Paddock"

    teks_menu = (
        f"🏁 **SELAMAT DATANG DI SADJIWA CIRCUIT** 🏁\n"
        f"Halo, **{nama}**! Status: *{status_user}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Pusat balap motor sirkuit & komunitas Telegram interaktif.\n\n"
        f"📋 **DAFTAR FITUR & PERINTAH BOT:**\n\n"
        f"🎮 **Menu Tombol Utama:**\n"
        f"• 🏍️ **Garasi Saya** : Cek kondisi motor, oli mesin, stat top speed, dan koin.\n"
        f"• 🏪 **Showroom F1 Drivers** : Beli motor paddock pembalap F1 pakai koin balap.\n"
        f"• 🎮 **Mini Games** : Main game sirkuit interaktif (Web App ada stir & gas) atau gacha part.\n"
        f"• ⚔️ **Balap Liar 1v1** : Adu drag race motormu lawan rider lain berhadiah koin.\n"
        f"• 🏆 **Leaderboard Paddock** : Cek klasemen Sultan Terkaya, Terajin Balapan, & Jawara Sirkuit.\n"
        f"• 💳 **Top Up Koin Asli** : Pembelian koin via DANA (Admin verifikasi manual).\n"
        f"• 🎁 **Klaim Hadiah Harian** : Ambil santunan cuma-cuma 💰 500 koin setiap hari.\n\n"
        f"💬 **Perintah Obrolan Grup:**\n"
        f"• `/pamer` : Pamerkan spek unit garasi & status kekayaanmu ke member grup.\n"
        f"• `/diskusi [topik]` : Buka forum obrolan teknis motor atau sirkuit di grup.\n"
        f"• `/leaderboard` : Munculkan papan peringkat juara paddock secara instan.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 *Pilih menu di bawah atau ketik perintah di atas untuk mulai:*"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🏍️ Garasi Saya"), types.KeyboardButton("🏪 Showroom F1 Drivers"))
    markup.row(types.KeyboardButton("🎮 Mini Games"), types.KeyboardButton("⚔️ Balap Liar 1v1"))
    markup.row(types.KeyboardButton("🏆 Leaderboard Paddock"), types.KeyboardButton("💳 Top Up Koin Asli"))
    markup.row(types.KeyboardButton("🎁 Klaim Hadiah Harian"))
    
    bot.reply_to(pesan, teks_menu, reply_markup=markup, parse_mode="Markdown")

# --- 2. GARASI RESMI ---
@bot.message_handler(func=lambda m: m.text == "🏍️ Garasi Saya")
def cek_garasi(pesan):
    user_id = str(pesan.from_user.id)
    data = load_data()

    if user_id not in data:
        bot.reply_to(pesan, "Ketik /start dulu ya buat pendaftaran!")
        return

    u = data[user_id]
    m = u["motor"]
    
    info = (
        f"🛠️ **GARASI RESMI - {u['nama']}** 🛠️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Saldo Koin: {u['koin']:,} koin\n"
        f"💳 Total Top Up: Rp{u.get('total_topup', 0):,}\n"
        f"🏁 Record Balap: {u.get('total_win', 0)} Menang / {u.get('total_race', 0)} Race\n\n"
        f"🏍️ **Unit Aktif:** {m['nama_motor']}\n"
        f"⚡ Top Speed: {m['speed']} km/h\n"
        f"🛢️ Oli Mesin: {m.get('oli', 100)}%\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(pesan, info, parse_mode="Markdown")

# --- 3. SHOWROOM F1 (FOTO + NAVIGASI) ---
@bot.message_handler(func=lambda m: m.text == "🏪 Showroom F1 Drivers")
def buka_showroom(pesan):
    tampilkan_motor(pesan.chat.id, "1")

def tampilkan_motor(chat_id, motor_id):
    katalog = load_katalog()
    if motor_id not in katalog:
        return

    m = katalog[motor_id]
    total_motor = len(katalog)
    idx = int(motor_id)

    teks = (
        f"🏎️ **SHOWROOM PADDOCK F1 [{motor_id}/{total_motor}]**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏍️ **{m['nama']}**\n"
        f"👤 Koleksi Rider: **{m['rider']}**\n"
        f"⚡ Top Speed: {m['speed']} km/h\n"
        f"💰 Harga: **{m['harga']:,} Koin**\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    markup = types.InlineKeyboardMarkup()
    baris_nav = []
    if idx > 1:
        baris_nav.append(types.InlineKeyboardButton("⬅️ Prev", callback_data=f"nav_{idx-1}"))
    baris_nav.append(types.InlineKeyboardButton("🛒 Beli Motor Ini", callback_data=f"buy_{motor_id}"))
    if idx < total_motor:
        baris_nav.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"nav_{idx+1}"))

    markup.row(*baris_nav)

    try:
        bot.send_photo(chat_id, m["foto"], caption=teks, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        bot.send_message(chat_id, teks, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("nav_"))
def navigasi_katalog(call):
    motor_id = call.data.split("_")[1]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    tampilkan_motor(call.message.chat.id, motor_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def beli_unit(call):
    motor_id = call.data.split("_")[1]
    katalog = load_katalog()
    m = katalog.get(motor_id)
    user_id = str(call.from_user.id)
    data = load_data()

    if user_id not in data or not m:
        return

    user = data[user_id]
    if user["koin"] < m["harga"]:
        bot.answer_callback_query(call.id, "Koin kamu kurang! Top up koin dulu yuk.", show_alert=True)
        return

    user["koin"] -= m["harga"]
    user["motor"] = {
        "nama_motor": m["nama"],
        "mesin_lvl": 1,
        "speed": m["speed"],
        "oli": 100
    }
    save_data(data)
    bot.answer_callback_query(call.id, "Sukses dibeli!")
    bot.send_message(call.message.chat.id, f"🎉 Selamat! Motor **{m['nama']}** resmi masuk garasimu!", parse_mode="Markdown")

# --- 4. MINI GAMES (WEB APP + GACHA PART) ---
@bot.message_handler(func=lambda m: m.text == "🎮 Mini Games")
def menu_minigame(pesan):
    markup = types.InlineKeyboardMarkup()
    btn_webapp = types.InlineKeyboardButton("🏎️ MAIN GAME SIRKUIT (STIR & GAS)", web_app=types.WebAppInfo(url=URL_MINIAPP_GAME))
    btn_gacha = types.InlineKeyboardButton("📦 Gacha Sparepart Misterius (💰 300)", callback_data="mg_gacha")
    
    markup.add(btn_webapp)
    markup.add(btn_gacha)

    teks = (
        "🎮 **PADDOCK ARCADE - SADJIWA CIRCUIT**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Siap turun ke sirkuit? Klik tombol di bawah buat buka game layar sentuh lengkap dengan stir dan pedal gas!"
    )
    bot.reply_to(pesan, teks, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "mg_gacha")
def gacha_part(call):
    user_id = str(call.from_user.id)
    data = load_data()

    if user_id not in data:
        return

    user = data[user_id]
    biaya = 300

    if user["koin"] < biaya:
        bot.answer_callback_query(call.id, "Koin kamu kurang dari 300!", show_alert=True)
        return

    user["koin"] -= biaya

    hadiah_gacha = [
        {"item": "Kabel Busi Racing", "speed": 5, "koin_bonus": 0},
        {"item": "Oli Sintetik Formula", "speed": 0, "koin_bonus": 200},
        {"item": "Filter Udara Racing", "speed": 8, "koin_bonus": 0},
        {"item": "Zonk (Busi Mati)", "speed": 0, "koin_bonus": 0},
        {"item": "Tabung NOS Mini (Langka!)", "speed": 25, "koin_bonus": 500}
    ]

    hasil = random.choice(hadiah_gacha)
    user["motor"]["speed"] += hasil["speed"]
    user["koin"] += hasil["koin_bonus"]
    save_data(data)

    teks = (
        f"📦 **KOTAK SPAREPART DIBUKA!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Dapat: **{hasil['item']}**\n"
        f"Bonus Top Speed: +{hasil['speed']} km/h\n"
        f"Bonus Koin: +💰 {hasil['koin_bonus']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Top Speed motormu sekarang: **{user['motor']['speed']} km/h**"
    )
    bot.edit_message_text(teks, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# --- 5. BALAP LIAR 1V1 ---
@bot.message_handler(func=lambda m: m.text == "⚔️ Balap Liar 1v1")
def balap_liar(pesan):
    user_id = str(pesan.from_user.id)
    data = load_data()

    if user_id not in data:
        bot.reply_to(pesan, "Ketik /start dulu ya!")
        return

    user = data[user_id]
    motor = user["motor"]
    taruhan = 300

    if user["koin"] < taruhan:
        bot.reply_to(pesan, f"Butuh minimal 💰 {taruhan} koin buat balapan!")
        return

    speed_lawan = random.randint(90, 250)
    nama_lawan = random.choice(["Rider Aspal", "Joki Liar", "Paddock Pro", "Pembalap F1 Trainee"])

    user["total_race"] = user.get("total_race", 0) + 1

    if motor["speed"] + random.randint(-15, 15) >= speed_lawan:
        user["koin"] += taruhan
        user["total_win"] = user.get("total_win", 0) + 1
        hasil = f"🏆 **MENANG RACE!**\nKamu ngalahin {nama_lawan}!\nHadiah: +💰 {taruhan:,} koin.\nTotal: 💰 {user['koin']:,}"
    else:
        user["koin"] -= taruhan
        hasil = f"💀 **KALAH RACE!**\n{nama_lawan} terlalu kencang.\nKoin: -💰 {taruhan:,}.\nSisa: 💰 {user['koin']:,}"

    save_data(data)
    bot.reply_to(pesan, hasil, parse_mode="Markdown")

# --- 6. LEADERBOARD / DASHBOARD PEMBALAP ---
@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard Paddock")
@bot.message_handler(commands=['leaderboard', 'top'])
def leaderboard(pesan):
    data = load_data()
    if not data:
        bot.reply_to(pesan, "Belum ada data pembalap yang terdaftar!")
        return

    users = list(data.values())

    top_sultan = sorted(users, key=lambda x: (x.get("total_topup", 0), x.get("koin", 0)), reverse=True)[:5]
    top_rajin = sorted(users, key=lambda x: x.get("total_race", 0), reverse=True)[:5]
    top_jago = sorted(users, key=lambda x: x.get("total_win", 0), reverse=True)[:5]

    teks = "🏆 **PADDOCK HALL OF FAME - SADJIWA CIRCUIT** 🏆\n━━━━━━━━━━━━━━━━━━━━\n\n"

    teks += "👑 **SULTAN PADDOCK (Top Up & Saldo):**\n"
    for i, u in enumerate(top_sultan, 1):
        motor_nama = u.get("motor", {}).get("nama_motor", "Vespa")
        teks += f"{i}. **{u['nama']}** — 💰 {u['koin']:,} Koin (Rp{u.get('total_topup', 0):,})\n   🏍️ *{motor_nama}*\n"

    teks += "\n🏎️ **PADDOCK WARRIOR (Paling Rajin Balapan):**\n"
    for i, u in enumerate(top_rajin, 1):
        teks += f"{i}. **{u['nama']}** — 🏁 {u.get('total_race', 0)}x Balapan\n"

    teks += "\n⚡ **KING OF CIRCUIT (Paling Sering Menang):**\n"
    for i, u in enumerate(top_jago, 1):
        winrate = round((u.get('total_win', 0) / u.get('total_race', 1)) * 100) if u.get('total_race', 0) > 0 else 0
        teks += f"{i}. **{u['nama']}** — 🏆 {u.get('total_win', 0)} Menang ({winrate}% WR)\n"

    teks += "━━━━━━━━━━━━━━━━━━━━"
    bot.reply_to(pesan, teks, parse_mode="Markdown")

# --- 7. TOP UP DANA ONLY (MANUAL APPROVAL ADMIN) ---
@bot.message_handler(func=lambda m: m.text == "💳 Top Up Koin Asli")
def menu_topup(pesan):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 5.000 Koin - Rp10.000", callback_data="topup_5k"))
    markup.add(types.InlineKeyboardButton("💰 15.000 Koin - Rp25.000", callback_data="topup_15k"))
    markup.add(types.InlineKeyboardButton("💰 35.000 Koin - Rp50.000", callback_data="topup_35k"))

    teks = (
        "💳 **TOP UP KOIN SADJIWA CIRCUIT**\n"
        "Silakan pilih nominal paket koin balap yang ingin kamu beli:"
    )
    bot.reply_to(pesan, teks, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("topup_"))
def instruksi_bayar(call):
    paket = call.data
    info = {
        "topup_5k": ("5.000 Koin", "Rp10.000", 5000, 10000),
        "topup_15k": ("15.000 Koin", "Rp25.000", 15000, 25000),
        "topup_35k": ("35.000 Koin", "Rp50.000", 35000, 50000)
    }[paket]

    teks = (
        f"📌 **PEMBAYARAN TOP UP (DANA ONLY)**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Paket: **{info[0]}**\n"
        f"Total Bayar: **{info[1]}**\n\n"
        f"Silakan transfer ke nomor DANA:\n"
        f"📱 **`083863830955`**\n"
        f"👤 A.N: **HAMZAH ABBAS / USER**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ **PENTING:** Setelah berhasil transfer, segera kirim **FOTO SCREENSHOT BUKTI TRANSFER** ke chat bot ini!"
    )
    bot.send_message(call.message.chat.id, teks, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_bukti_transfer(pesan):
    user_id = pesan.from_user.id
    nama = pesan.from_user.first_name
    file_id = pesan.photo[-1].file_id

    markup = types.InlineKeyboardMarkup()
    btn_acc5k = types.InlineKeyboardButton("✅ Setujui Rp10K (+5K Koin)", callback_data=f"acc_{user_id}_5000_10000")
    btn_acc15k = types.InlineKeyboardButton("✅ Setujui Rp25K (+15K Koin)", callback_data=f"acc_{user_id}_15000_25000")
    btn_acc35k = types.InlineKeyboardButton("✅ Setujui Rp50K (+35K Koin)", callback_data=f"acc_{user_id}_35000_50000")
    markup.add(btn_acc5k)
    markup.add(btn_acc15k, btn_acc35k)

    caption_admin = f"🚨 **BUKTI TOP UP DANA MASUK!**\nUser: {nama} (ID: `{user_id}`)\nPilih persetujuan sesuai nominal transfer:"
    try:
        bot.send_photo(ADMIN_ID, file_id, caption=caption_admin, reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(pesan, "✅ Bukti transfer sudah diteruskan ke Admin! Saldo akan masuk otomatis setelah disetujui.")
    except Exception:
        bot.reply_to(pesan, "⚠️ Gagal mengirim bukti ke Admin.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("acc_"))
def approve_topup(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Kamu bukan admin!", show_alert=True)
        return

    _, target_user, jumlah_koin, rupiah = call.data.split("_")
    jumlah_koin = int(jumlah_koin)
    rupiah = int(rupiah)
    data = load_data()

    if target_user in data:
        data[target_user]["koin"] += jumlah_koin
        data[target_user]["total_topup"] = data[target_user].get("total_topup", 0) + rupiah
        save_data(data)
        bot.send_message(int(target_user), f"🎉 **Top Up Berhasil!**\nSaldo **+{jumlah_koin:,} Koin** telah masuk ke akun garasimu!", parse_mode="Markdown")
        bot.edit_message_caption(f"✅ TOP UP TELAH DISETUJUI ADMIN (Rp{rupiah:,})", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id, "Sukses dikonfirmasi!")

# --- 8. FORUM & DISKUSI GRUP ---
@bot.message_handler(commands=['diskusi', 'tanya'])
def forum_diskusi(pesan):
    argumen = pesan.text.split(maxsplit=1)
    if len(argumen) < 2:
        bot.reply_to(
            pesan, 
            "💬 **CARA BIKIN DISKUSI PADDOCK:**\n"
            "Ketik: `/diskusi [topik atau pertanyaanmu]`\n\n"
            "Contoh:\n`/diskusi Rekomendasi oli racing buat trek lurus apa ya?`",
            parse_mode="Markdown"
        )
        return

    topik = argumen[1]
    format_diskusi = (
        f"📢 **PADDOCK FORUM DISKUSI**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Pemantik: **{pesan.from_user.first_name}**\n"
        f"💬 Topik: *\"{topik}\"*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 Reply pesan ini untuk mulai berdiskusi bareng member lain!"
    )
    bot.send_message(pesan.chat.id, format_diskusi, parse_mode="Markdown")

@bot.message_handler(commands=['pamer'])
def pamer_motor(pesan):
    user_id = str(pesan.from_user.id)
    data = load_data()

    if user_id not in data:
        bot.reply_to(pesan, "Kamu belum terdaftar di garasi! Ketik /start di private chat bot dulu ya.")
        return

    user = data[user_id]
    m = user["motor"]

    teks_pamer = (
        f"🔥 **PAMER SPEK UNIT - {user['nama'].upper()}** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏍️ Unit: **{m['nama_motor']}**\n"
        f"⚡ Top Speed: **{m['speed']} km/h**\n"
        f"⚙️ Mesin: Level {m['mesin_lvl']}\n"
        f"💰 Kekayaan: 💰 {user['koin']:,} Koin\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(pesan.chat.id, teks_pamer, parse_mode="Markdown")

# --- 9. HADIAH HARIAN ---
@bot.message_handler(func=lambda m: m.text == "🎁 Klaim Hadiah Harian")
def daily(pesan):
    user_id = str(pesan.from_user.id)
    data = load_data()
    if user_id in data:
        data[user_id]["koin"] += 500
        save_data(data)
        bot.reply_to(pesan, f"🎉 Dapet santunan modal +500 koin! Total: 💰 {data[user_id]['koin']:,}")

# --- JALANKAN BOT ---
print("Bot Sadjiwa Circuit siap balapan...")
bot.infinity_polling()
