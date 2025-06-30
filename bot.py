from collections import defaultdict
postlar = defaultdict(list)
import telebot
from telebot import types
import time
import os
import json

def init_json_file(filename):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

init_json_file("feedback_comments.json")

def yukla_mahsulotlar():
    try:
        with open("products.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

from datetime import datetime

import telebot
from data.config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
foydalanuvchi_buyurtmalari = {}
postlar = defaultdict(list)

def save_comment(message):
    izoh = {
        "user_id": message.from_user.id,
        "username": message.from_user.username or "no_username",
        "comment": message.text,
        "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open("feedback_comments.json", "r", encoding="utf-8") as f:
            all_comments = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_comments = []

    all_comments.append(izoh)

    with open("feedback_comments.json", "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=4)

    bot.send_message(message.chat.id, "✅ Rahmat! Izohingiz qabul qilindi.")

narxlar = {
    "stars_50":  ("50 ta Telegram Stars", "14,999 so‘m"),
    "stars_75":  ("75 ta Telegram Stars", "19,999 so‘m"),
    "stars_100":  ("100 ta Telegram Stars", "24,999 so‘m"),
    "stars_150":  ("150 ta Telegram Stars", "34,999 so‘m"),
    "stars_250":  ("250 ta Telegram Stars", "54,999 so‘m"),
    "stars_350":  ("350 ta Telegram Stars", "69,999 so‘m"),
    "stars_500":  ("500 ta Telegram Stars", "99,999 so‘m"),
    "stars_750":  ("750 ta Telegram Stars", "144,999 so‘m"),
    "stars_1000": ("1000 ta Telegram Stars", "189,999 so‘m"),
    "stars_1500": ("1500 ta Telegram Stars", "284,999 so‘m"),
    "stars_2500": ("2500 ta Telegram Stars", "469,999 so‘m"),
    "stars_5000": ("5000 ta Telegram Stars", "934,999 so‘m"),
    "stars_10000": ("10000 ta Telegram Stars", "1,864,999 so‘m"),
    "premium_in_1": ("1 oylik Premium (akkaunt ichidan)", "39,999 so‘m"),
    "premium_in_12": ("1 yillik Premium (akkaunt ichidan)", "249,999 so‘m"),
    "premium_out_3": ("3 oylik Premium (akkauntga kirmasdan)", "154,999 so‘m"),
    "premium_out_6": ("6 oylik Premium (akkauntga kirmasdan)", "204,999 so‘m"),
    "premium_out_12": ("1 yillik Premium (akkauntga kirmasdan)", "324,999 so‘m"),
}

def update_log_status(user_id, yangi_status):
    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    for log in reversed(logs):
        if log["user_id"] == user_id:
            log["status"] = yangi_status
            break

    with open("buyurtmalar_log.json", "w", encoding="utf-8") as file:
        json.dump(logs, file, ensure_ascii=False, indent=4)

def feedback_buttons():
    markup = types.InlineKeyboardMarkup()
    for i in range(1, 6):
        markup.add(types.InlineKeyboardButton("⭐️" * i, callback_data=f"feedback_{i}"))
    return markup

def mahsulotlar_menusi():
    markup = types.InlineKeyboardMarkup(row_width=2)
    mahsulotlar = yukla_mahsulotlar().get("stars", {})

    for nom, narx in mahsulotlar.items():
        tugma = types.InlineKeyboardButton(f"{nom} – {narx}", callback_data=nom)
        markup.add(tugma)

    return markup

def premium_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    mahsulotlar = yukla_mahsulotlar().get("premium", {})

    for nom, narx in mahsulotlar.items():
        tugma = types.InlineKeyboardButton(f"{nom} – {narx}", callback_data=nom)
        markup.add(tugma)

    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🟡 Telegram Stars", "🔵 Telegram Premium")
    markup.add("ℹ️ Biz haqimizda", "🆘 Yordam")
    
    bot.send_message(message.chat.id,
        "👋 Assalomu alaykum, *JalolShop* botiga xush kelibsiz!\n\nXizmat turini tanlang 👇",
        reply_markup=markup, parse_mode='Markdown')

    try:
            with open("users.json", "r", encoding="utf-8") as file:
                users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
                users = []

    if message.from_user.id not in users:
        users.append(message.from_user.id)
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if len(message.text.split()) > 1:
        referer_id = message.text.split()[1] 

        if referer_id != str(user_id): 
            try:
                with open("referrals.json", "r", encoding="utf-8") as file:
                    referrals = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                referrals = {}

            if referer_id not in referrals:
                referrals[referer_id] = []

            if user_id not in referrals[referer_id]:
                referrals[referer_id].append(user_id)

                with open("referrals.json", "w", encoding="utf-8") as file:
                    json.dump(referrals, file, ensure_ascii=False, indent=4)

                if len(referrals[referer_id]) == 10:
                    bot.send_message(int(referer_id),
                        "🎉 Tabriklaymiz! Siz 10 ta do‘stingizni taklif qildingiz!\n💫 Mukofot: 50 ta Stars")
                    bot.send_message(5092720090,
                        f"⭐️ 10 ta referal! @{message.from_user.username}ga mukofot yuboring!")

                elif len(referrals[referer_id]) == 100:
                    bot.send_message(int(referer_id),
                        "🏆 Ajoyib! Siz 100 ta do‘stingizni taklif qildingiz!\n💎 Mukofot: 500 ta Stars")
                    bot.send_message(5092720090,
                        f"🏅 100 ta referal! @{message.from_user.username}ga SUPER mukofot yuboring!")

    bot.send_message(message.chat.id, "👋 Xush kelibsiz JalolShop’ga!")

@bot.message_handler(func=lambda m: m.text == "🟡 Telegram Stars")
def stars_menu(message):
    markup = mahsulotlar_menusi()
    bot.send_message(message.chat.id, "💫 Mahsulotlardan birini tanlang:", reply_markup=markup)
 
@bot.message_handler(func=lambda m: m.text == "🔵 Telegram Premium")
def show_premium_menu(message):
    markup = premium_menu()
    bot.send_message(message.chat.id, "💎 Telegram Premium paketlaridan birini tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Biz haqimizda")
def about(message):
    bot.send_message(message.chat.id,
        "📦 *JalolShop* — avtomatik Telegram xizmatlari do‘koni.\n"
        "🛍️ Stars, Premium va boshqa xizmatlar 24/7 sotuvda.", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🆘 Yordam")
def help_menu(message):
    bot.send_message(message.chat.id,
        "🆘 *Yordam kerakmi?* Quyidagilarga murojaat qiling:\n"
        "👤 Admin: [@jaloI_admin](https://t.me/jaloI_admin)\n"
        "📢 Kanal: [@JalolShopOfficial](https://t.me/JalolShopOfficial)\n"
        "✉️ Email: Mirjalol.Tech@gmail.com", parse_mode='Markdown', disable_web_page_preview=True)

@bot.message_handler(commands=['adminpanel'])
def admin_panel(message):
    admin_id = 5092720090
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")
        return

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("➕ Stars qo‘shish", callback_data="add_stars"),
        types.InlineKeyboardButton("➕ Premium qo‘shish", callback_data="add_premium"),
    )
    keyboard.add(
        types.InlineKeyboardButton("🗑 Mahsulot o‘chirish", callback_data="admin_delete_product"),
    )
    keyboard.add(
        types.InlineKeyboardButton("📤 Excelga yuklab olish", callback_data="admin_export_excel"),
        types.InlineKeyboardButton("🧹 Eski loglarni tozalash", callback_data="admin_clean_logs")
    )
    keyboard.add(
    types.InlineKeyboardButton("📈 Grafik statistika", callback_data="admin_grafik")
    )

    keyboard.add(
        types.InlineKeyboardButton("📣 Reklama yuborish", callback_data="admin_broadcast")
    )

    bot.send_message(message.chat.id, "🔧 Admin boshqaruv paneli:", reply_markup=keyboard)

@bot.message_handler(commands=['stats'])
def stats(message):
    admin_id = 5092720090
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")
        return

    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    jami = len(logs)
    tasdiqlangan = sum(1 for log in logs if log.get("status") == "Tasdiqlandi✅")
    bekor_qilingan = sum(1 for log in logs if log.get("status") == "Rad etildi❌")
    kutmoqda = sum(1 for log in logs if log.get("status") == "Kutmoqda")

    javob = (
        "📊 <b>Buyurtmalar statistikasi</b>\n\n"
        f"<b>Jami:</b> {jami} ta\n"
        f"✅ <b>Tasdiqlangan:</b> {tasdiqlangan} ta\n"
        f"❌ <b>Rad etilgan:</b> {bekor_qilingan} ta\n"
        f"⏳ <b>Kutmoqda:</b> {kutmoqda} ta"
    )

    bot.send_message(message.chat.id, javob, parse_mode='HTML')

@bot.message_handler(commands=['feedbackstats'])
def show_feedback_stats(message):
    if message.from_user.id != 5092720090:
        return bot.send_message(message.chat.id, "⛔ Siz admin emassiz.")

    try:
        with open("feedback_log.json", "r", encoding="utf-8") as f:
            feedbacklar = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return bot.send_message(message.chat.id, "❗️ Hali hech qanday fikr-mulohaza yo‘q.")

    jami = len(feedbacklar)
    if jami == 0:
        return bot.send_message(message.chat.id, "❗️ Hali hech kim baho bermagan.")

    ortacha = sum([fb["baho"] for fb in feedbacklar]) / jami
    matn = (
        f"📊 <b>Fikr-mulohaza statistikasi</b>\n\n"
        f"👥 Umumiy foydalanuvchilar: <b>{jami}</b>\n"
        f"⭐️ O‘rtacha baho: <b>{round(ortacha, 2)}</b>"
    )
    bot.send_message(message.chat.id, matn, parse_mode='HTML')



@bot.message_handler(commands=['topbuyers'])
def show_top_buyers(message):
    if message.from_user.id != 5092720090:
        return bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")
    
    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return bot.send_message(message.chat.id, "❗️ Buyurtmalar log fayli topilmadi.")

    user_counts = {}
    usernames = {}

    for log in logs:
        user_id = log["user_id"]
        user_counts[user_id] = user_counts.get(user_id, 0) + 1
        usernames[user_id] = log.get("username", "Nomaʼlum")

    if not user_counts:
        return bot.send_message(message.chat.id, "🛒 Hali hech kim xarid qilmagan.")

    sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    text = "<b>🏆 TOP xaridorlar:</b>\n\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        username = usernames[user_id]
        text += f"{i}. @{username} — {count} ta buyurtma\n"

    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=['refstats'])
def ref_stats(message):
    admin_id = 5092720090 
    if message.from_user.id != admin_id:
        return bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")

    try:
        with open("referrals.json", "r", encoding="utf-8") as f:
            referrals = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return bot.send_message(message.chat.id, "❗️ Referal ma'lumotlari topilmadi.")

    jami_foydalanuvchi = len(referrals)
    jami_referal = sum(len(v) for v in referrals.values())

    matn = (
        f"📈 <b>Referal statistikasi</b>\n\n"
        f"👤 Refererlar soni: <b>{jami_foydalanuvchi}</b>\n"
        f"👥 Umumiy taklif qilinganlar: <b>{jami_referal}</b>"
    )
    bot.send_message(message.chat.id, matn, parse_mode="HTML")

@bot.message_handler(commands=['referal'])
def referal_link(message):
    user_id = message.from_user.id
    username = bot.get_me().username  

    link = f"https://t.me/{username}?start={user_id}"
    bot.send_message(message.chat.id,
        f"🔗 Sizning taklif havolangiz:\n{link}\n\n"
        "Ushbu havolani do‘stlaringizga yuboring va bonuslar yutib oling!")

@bot.message_handler(commands=['profile'])
def show_profile(message):
    user_id = message.from_user.id
    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    try:
        with open("feedback_log.json", "r", encoding="utf-8") as f:
            feedbacks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        feedbacks = []

    user_logs = [log for log in logs if log["user_id"] == user_id]
    user_feedbacks = [f for f in feedbacks if f["user_id"] == user_id]

    if not user_logs:
        bot.send_message(user_id, "❗️Siz hali hech qanday buyurtma qilmagansiz.")
        return

    oxirgi = user_logs[-1]
    buyurtmalar_soni = len(user_logs)
    oxirgi_baho = user_feedbacks[-1]["baho"] if user_feedbacks else "❌ Baho yo‘q"

    text = (
        f"👤 <b>Foydalanuvchi profili</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"🔹 Ism: <b>{message.from_user.first_name}</b>\n"
        f"🔸 Username: @{message.from_user.username or 'yo‘q'}\n\n"
        f"🛍 Buyurtmalar soni: <b>{buyurtmalar_soni}</b>\n"
        f"⭐️ Oxirgi baho: <b>{oxirgi_baho}</b>\n\n"
        f"📦 Oxirgi buyurtma:\n"
        f" - Mahsulot: <b>{oxirgi['mahsulot']}</b>\n"
        f" - Narx: <b>{oxirgi['narx']}</b>\n"
        f" - Holat: <b>{oxirgi['status']}</b>\n"
        f" - Sana: <code>{oxirgi['vaqt']}</code>"
    )
    bot.send_message(user_id, text, parse_mode='HTML')


@bot.message_handler(commands=['bonuslarim'])
def bonuslarim(message):
    user_id = str(message.from_user.id)
    
    try:
        with open("referrals.json", "r", encoding="utf-8") as f:
            referrals = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        referrals = {}

    taklif_soni = len(referrals.get(user_id, []))

    mukofot_10 = "✅ Olingan" if taklif_soni >= 10 else "❌ Hali yo‘q"
    mukofot_100 = "✅ Olingan" if taklif_soni >= 100 else "❌ Hali yo‘q"

    matn = (
        f"🎁 <b>Bonuslarim</b>\n\n"
        f"👥 Taklif qilgan do‘stlar soni: <b>{taklif_soni} ta</b>\n\n"
        f"🏅 10 ta do‘st uchun 50 Stars: {mukofot_10}\n"
        f"🏆 100 ta do‘st uchun 500 Stars: {mukofot_100}"
    )

    bot.send_message(message.chat.id, matn, parse_mode="HTML")

@bot.message_handler(commands=['izohlar'])
def show_comments(message):
    admin_id = 5092720090

    if message.from_user.id != admin_id:
        return bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")

    try:
        with open("feedback_comments.json", "r", encoding="utf-8") as f:
            izohlar = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return bot.send_message(admin_id, "❗️ Hech qanday izoh topilmadi.")

    if not izohlar:
        return bot.send_message(admin_id, "📭 Hali izohlar yo‘q.")

    for i in range(0, len(izohlar), 5):
        matn = "📝 <b>Foydalanuvchi izohlari:</b>\n\n"
        for izoh in izohlar[i:i+5]:
            matn += (
                f"👤 <b>@{izoh.get('username', 'no_username')}</b>\n"
                f"💬 {izoh['comment']}\n"
                f"🕒 {izoh['vaqt']}\n\n"
            )
        bot.send_message(admin_id, matn, parse_mode='HTML')




def log_buyurtma(user, nom, narx, rasm_id):
    log_entry = {
        "username": user.username,
        "first_name": user.first_name,
        "user_id": user.id,
        "mahsulot": nom,
        "narx": narx,
        "rasm_id": rasm_id,
        "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Kutmoqda"
    }

    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append(log_entry)

    with open("buyurtmalar_log.json", "w", encoding="utf-8") as file:
        json.dump(logs, file, ensure_ascii=False, indent=4)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user = message.from_user
    user_id = user.id

    try:
        with open("cooldowns.json", "r", encoding="utf-8") as f:
            cooldowns = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        cooldowns = {}

    now = time.time()
    if str(user_id) in cooldowns and now < cooldowns[str(user_id)]:
        qolgan = int(cooldowns[str(user_id)] - now)
        min, sec = divmod(qolgan, 60)
        bot.send_message(user_id, f"⏱️ Siz keyingi buyurtmani {int(min)} daqiqa {int(sec)} soniyadan so‘ng yuborishingiz mumkin.")
        return

    if not user.username:
        bot.send_message(user_id, "❗️Sizda Telegram username yo‘q. Buyurtma bekor qilindi. \n\n 🆘Yordam: @jaloI_admin")
        warning = (
            f"🚫 <b>Buyurtma bekor qilindi</b>\n"
            f"Sabab: Foydalanuvchida username yo‘q\n"
            f"🆔 ID: <code>{user.id}</code>"
        )
        bot.send_message(5092720090, warning, parse_mode='HTML') 
        return

    if foydalanuvchi_buyurtmalari.get(user_id, {}).get("active") == True:
        bot.reply_to(message, "⚠️ Siz allaqachon chek yuborgansiz. Iltimos, admin tasdiqlaguncha kuting.")
        return

    if user_id not in foydalanuvchi_buyurtmalari:
        bot.reply_to(message, "❗️Avval mahsulotni tanlang va keyin to‘lov screenshotini yuboring.")
        return

    buyurtma = foydalanuvchi_buyurtmalari[user_id]
    nom = buyurtma["nom"]
    narx = buyurtma["narx"]
    rasm_id = message.photo[-1].file_id

    user_info = f"👤 Foydalanuvchi: @{user.username} ({user.first_name})\n🆔 ID: <code>{user_id}</code>"
    caption = f"📥 <b>Yangi buyurtma!</b>\n\n{user_info}\n💰 To'lov summasi: <b>{narx}</b>\n🛒 Mahsulot: <b>{nom}</b>"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"tasdiq_{user_id}"),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"bekor_{user_id}")
    )

    bot.reply_to(message, "✅ Chek qabul qilindi. Xizmat holatini @JalolShopOfficial kanalida kuzatib boring.")

    admin_id = 5092720090
    kanal_id = "@JalolShopOfficial"

    admin_msg = bot.send_photo(admin_id, rasm_id, caption=caption, parse_mode='HTML', reply_markup=markup)
    kanal_msg = bot.send_photo(kanal_id, rasm_id, caption=caption, parse_mode='HTML', reply_markup=markup)

    postlar[user_id] = {
        "kanal_chat_id": kanal_id,
        "kanal_msg_id": kanal_msg.message_id,
        "admin_msg_id": admin_msg.message_id,
        "admin_chat_id": admin_id,
        "nom": nom,
        "narx": narx,
        "username": user.username,
        "first_name": user.first_name
    }

    foydalanuvchi_buyurtmalari[user_id]["active"] = True

    log_buyurtma(user, nom, narx, rasm_id)

from openpyxl import Workbook
from datetime import datetime
import os

def export_log(message):
    admin_id = 5092720090

    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        bot.send_message(admin_id, "❗️ Buyurtma loglari topilmadi yoki bo‘sh.")
        return

    if not logs:
        bot.send_message(admin_id, "📁 Hozircha hech qanday buyurtma yo‘q.")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Buyurtmalar"

    ws.append(["Username", "Ism", "ID", "Mahsulot nomi", "Narxi", "Status", "Vaqt"])

    for log in logs:
        ws.append([
            f"@{log.get('username', 'yo‘q')}",
            log.get("first_name", ""),
            log.get("user_id", ""),
            log.get("mahsulot", ""),
            log.get("narx", ""),
            log.get("status", ""),
            log.get("vaqt", "")
        ])

    fayl_nomi = f"buyurtmalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    path = f"./{fayl_nomi}"
    wb.save(path)

    with open(path, "rb") as f:
        bot.send_document(admin_id, f, caption="✅ Buyurtmalar Excel fayli tayyor!")

    os.remove(path)
    


import matplotlib.pyplot as plt

def rasmli_statistika_yaratish():
    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except:
        return None

    tasdiq = sum(1 for l in logs if l.get("status") == "Tasdiqlandi✅")
    bekor = sum(1 for l in logs if l.get("status") == "Rad etildi❌")
    kutmoqda = sum(1 for l in logs if l.get("status") == "Kutmoqda")

    labels = ['✅ Tasdiqlandi', '❌ Rad etildi', '⏳ Kutmoqda']
    values = [tasdiq, bekor, kutmoqda]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title('Buyurtmalar Statistkasi (Diagramma)')
    plt.axis('equal')

    image_path = "statistika_diagramma.png"
    plt.savefig(image_path)
    plt.close()
    return image_path





        
@bot.callback_query_handler(func=lambda call: call.data.startswith("tasdiq_") or call.data.startswith("bekor_"))
def handle_admin_actions(call):
    user_id = int(call.data.split("_")[1])
    data = postlar.get(user_id)

    if not data:
        return

    if call.from_user.id != data["admin_chat_id"]:
        bot.answer_callback_query(call.id, "❌ Sizda bu amalni bajarishga ruxsat yo‘q.", show_alert=True)
        return

    if call.data.startswith("tasdiq_"):
        update_log_status(user_id, "Tasdiqlandi✅")

        tasdiqlangan_caption = (
            f"🛍 <b>Buyurtma holati:</b>\n\n"
            f"👤 Foydalanuvchi: @{data['username']} ({data['first_name']})\n"
            f"🆔 ID: <code>{user_id}</code>\n\n"
            f"📦 Mahsulot: <b>{data['nom']}</b>\n"
            f"💰 Narx: <b>{data['narx']}</b>\n\n"
            f"✅ <b>To‘lov tasdiqlandi.</b>"
        )

        bot.edit_message_caption(chat_id=data["kanal_chat_id"], message_id=data["kanal_msg_id"],
                                 caption=tasdiqlangan_caption, parse_mode='HTML')
        bot.edit_message_caption(chat_id=data["admin_chat_id"], message_id=data["admin_msg_id"],
                                 caption=tasdiqlangan_caption, parse_mode='HTML')

        if user_id in foydalanuvchi_buyurtmalari:
            foydalanuvchi_buyurtmalari[user_id]["active"] = False

        feedback_markup = types.InlineKeyboardMarkup()
        for i in range(1, 6):
            feedback_markup.add(types.InlineKeyboardButton("⭐️" * i, callback_data=f"feedback_{i}"))
        bot.send_message(user_id, "🗣 Xizmatdan qoniqdingizmi?\n1 dan 5 gacha baholang:", reply_markup=feedback_markup)

        try:
            with open("cooldowns.json", "r", encoding="utf-8") as f:
                cooldowns = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cooldowns = {}

        cooldowns[str(user_id)] = time.time() + 120

        with open("cooldowns.json", "w", encoding="utf-8") as f:
            json.dump(cooldowns, f, indent=4)

    elif call.data.startswith("bekor_"):
        update_log_status(user_id, "Rad etildi❌")

        bot.delete_message(chat_id=data["kanal_chat_id"], message_id=data["kanal_msg_id"])
        bot.delete_message(chat_id=data["admin_chat_id"], message_id=data["admin_msg_id"])

        bot.send_message(user_id,
            "❌ Sizning to‘lovingiz rad etildi. Iltimos, qaytadan urinib ko‘ring.\n"
            "🆘 Savollar uchun: @jaloI_admin")

        if user_id in foydalanuvchi_buyurtmalari:
            foydalanuvchi_buyurtmalari[user_id]["active"] = False

        try:
            with open("cooldowns.json", "r", encoding="utf-8") as f:
                cooldowns = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cooldowns = {}

        cooldowns[str(user_id)] = time.time() + 1800 

        with open("cooldowns.json", "w", encoding="utf-8") as f:
            json.dump(cooldowns, f, indent=4)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def mahsulot_kiritish_bosqichi(call):
    if call.from_user.id != 5092720090:
        return
    kategoriya = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, f"➕ Yangi mahsulotni {kategoriya} bo‘limiga kiriting:\n\nFormat: Nomi - Narxi", parse_mode="Markdown")
    
    bot.register_next_step_handler(msg, lambda m: saqlash_mahsulot(m, kategoriya))

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_product")
def admin_add_product(call):
    if call.from_user.id != 5092720090:
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🟡 Stars bo‘limi", callback_data="add_stars"),
        types.InlineKeyboardButton("🔵 Premium bo‘limi", callback_data="add_premium")
    )
    bot.send_message(call.message.chat.id, "Qaysi bo‘limga mahsulot qo‘shmoqchisiz?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_delete_product")
def mahsulot_ochirish(call):
    if call.from_user.id != 5092720090:
        return

    mahsulotlar = yukla_mahsulotlar()
    tugmalar = types.InlineKeyboardMarkup()

    for kategoriya, items in mahsulotlar.items():
        for nom in items:
            tugmalar.add(types.InlineKeyboardButton(f"{nom}", callback_data=f"delete_{kategoriya}_{nom}"))

    bot.send_message(call.message.chat.id, "🗑 O‘chirish uchun mahsulotni tanlang:", reply_markup=tugmalar)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def mahsulot_ni_ochir(call):
    if call.from_user.id != 5092720090:
        return

    _, kategoriya, nom = call.data.split("_", 2)
    mahsulotlar = yukla_mahsulotlar()

    if kategoriya in mahsulotlar and nom in mahsulotlar[kategoriya]:
        del mahsulotlar[kategoriya][nom]
        with open("products.json", "w", encoding="utf-8") as file:
            json.dump(mahsulotlar, file, ensure_ascii=False, indent=4)
        bot.answer_callback_query(call.id, f"✅ '{nom}' o‘chirildi.")
        bot.edit_message_text("✅ Mahsulot muvaffaqiyatli o‘chirildi.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Mahsulot topilmadi.")

@bot.callback_query_handler(func=lambda call: call.data == "admin_export_excel")
def handle_export_excel(call):
    export_log(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "admin_clean_logs")
def handle_clean_logs(call):
    admin_id = 5092720090

    try:
        with open("buyurtmalar_log.json", "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
        bot.send_message(admin_id, "🧹 Eski buyurtma loglari tozalandi.")
    except Exception as e:
        bot.send_message(admin_id, f"❗️ Log faylni tozalashda xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_grafik")
def send_graph(call):
    if call.from_user.id != 5092720090:
        return
    image_path = rasmli_statistika_yaratish()
    if image_path:
        with open(image_path, "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, caption="📊 Grafik ko‘rinishdagi statistika")
        os.remove(image_path)
    else:
        bot.send_message(call.message.chat.id, "❌ Statistika fayli topilmadi.")

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def start_broadcast(call):
    if call.from_user.id != 5092720090:
        return
    msg = bot.send_message(call.message.chat.id, "📣 Reklama matnini yuboring:")
    bot.register_next_step_handler(msg, process_broadcast)

@bot.callback_query_handler(func=lambda call: call.data.startswith("feedback_"))
def handle_feedback(call):
    user_id = call.from_user.id
    baho = int(call.data.split("_")[1])

    bot.answer_callback_query(call.id, f"Rahmat! Siz {baho} ⭐️ baho berdingiz.", show_alert=True)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    feedback = {
        "user_id": user_id,
        "username": call.from_user.username,
        "baho": baho,
        "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open("feedback_log.json", "r", encoding="utf-8") as f:
            feedbacklar = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        feedbacklar = []

    feedbacklar.append(feedback)

    with open("feedback_log.json", "w", encoding="utf-8") as f:
        json.dump(feedbacklar, f, ensure_ascii=False, indent=4)

    admin_id = 5092720090
    bot.send_message(admin_id, f"📝 @{call.from_user.username} {baho} ⭐️ baho berdi.")

def process_broadcast(message):
    try:
        with open("users.json", "r", encoding="utf-8") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        bot.send_message(message.chat.id, "❗️ Hech qanday foydalanuvchi topilmadi.")
        return

    sent = 0
    failed = 0
    for user_id in users:
        try:
            bot.send_message(user_id, message.text)
            sent += 1
        except Exception:
            failed += 1

    bot.send_message(message.chat.id,
        f"✅ Reklama yakunlandi.\n\n📤 Yuborildi: {sent} ta\n❌ Yuborib bo‘lmadi: {failed} ta")

@bot.callback_query_handler(func=lambda call: True)
def handle_product_selection(call):
    user_id = call.from_user.id
    mahsulotlar = yukla_mahsulotlar()

    for kategoriya in mahsulotlar:
        if call.data in mahsulotlar[kategoriya]:
            nom = call.data
            narx = mahsulotlar[kategoriya][nom]

            foydalanuvchi_buyurtmalari[user_id] = {
                "nom": nom,
                "narx": narx
            }

            matn = (
                f"🛒 Siz tanladingiz: <b>{nom}</b>\n"
                f"💰 Narx: <b>{narx}</b>\n\n"
                "💳 <b>To‘lov kartalari:</b>\n"
                "🤵‍♀️ <b>Diyoraxon Valijonova</b>\n\n"
                "<b>Uzcard –</b> <code>5440 8100 0841 2388</code>\n"
                "<b>Humo –</b> <code>9860 1966 0138 0989</code>\n\n"
                "(Nusxalash uchun – 📋 Raqam ustiga bosing)\n\n"
                "✅ To‘lovni amalga oshirib, screenshot yuboring."
            )

            bot.send_message(user_id, matn, parse_mode='HTML')
            break

def saqlash_mahsulot(message, kategoriya): 
    if message.from_user.id != 5092720090:
        return

    if "-" not in message.text:
        bot.reply_to(message, "❌ Noto‘g‘ri format. Iltimos, Nomi - Narxi ko‘rinishida yozing.")
        return

    nom, narx = map(str.strip, message.text.split("-", 1))

    mahsulotlar = yukla_mahsulotlar()

    if kategoriya not in mahsulotlar:
        mahsulotlar[kategoriya] = {}

    mahsulotlar[kategoriya][nom] = narx

    with open("products.json", "w", encoding="utf-8") as file:
        json.dump(mahsulotlar, file, ensure_ascii=False, indent=4)

    bot.send_message(message.chat.id, f"✅ Mahsulot qo‘shildi:\n\n<b>{nom}</b> – <b>{narx}</b>", parse_mode='HTML')

@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    user_logs = [log for log in logs if log["user_id"] == user_id]
    if not user_logs:
        bot.send_message(user_id, "❗️Hech qanday buyurtma topilmadi.")
        return

    oxirgi = user_logs[-1]
    matn = (
        f"📦 Mahsulot: {oxirgi['mahsulot']}\n"
        f"💰 Narx: {oxirgi['narx']}\n"
        f"📅 Sana: {oxirgi['vaqt']}\n"
        f"📊 Holat: {'✅ Tasdiqlandi' if oxirgi['status'] == 'Tasdiqlandi' else ('❌ Rad etildi' if oxirgi['status'] == 'Rad etildi' else '⏳ Kutmoqda')}"
    )

    bot.send_message(user_id, matn)

    bot.send_message(user_id,
        "🗣 Xizmatdan qoniqdingizmi?\nIltimos, 1 dan 5 gacha baho bering ⭐️",
        reply_markup=feedback_buttons())

@bot.message_handler(commands=['adminpanel'])
def admin_panel(message):
    admin_id = 5092720090
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "⛔ Siz admin emassiz.")
        return

    try:
        with open("buyurtmalar_log.json", "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    jami = len(logs)
    tasdiqlangan = sum(1 for log in logs if log.get("status") == "Tasdiqlandi✅")
    bekor_qilingan = sum(1 for log in logs if log.get("status") == "Rad etildi❌")
    kutmoqda = sum(1 for log in logs if log.get("status") == "Kutmoqda")

    javob = (
        "📊 <b>Buyurtmalar statistikasi</b>\n\n"
        f"<b>Jami:</b> {jami} ta\n"
        f"✅ <b>Tasdiqlangan:</b> {tasdiqlangan} ta\n"
        f"❌ <b>Rad etilgan:</b> {bekor_qilingan} ta\n"
        f"⏳ <b>Kutmoqda:</b> {kutmoqda} ta"
    )

    bot.send_message(message.chat.id, javob, parse_mode='HTML')

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("📥 Mahsulot qo‘shish", callback_data="admin_add_product"),
        types.InlineKeyboardButton("🗑 Mahsulot o‘chirish", callback_data="admin_delete_product"),
        types.InlineKeyboardButton("📤 Excelga yuklab olish", callback_data="admin_export_excel"),
        types.InlineKeyboardButton("🧹 Eski loglarni tozalash", callback_data="admin_clean_logs")
    )

    bot.send_message(message.chat.id, "🔧 Qo‘shimcha admin funksiyalar:", reply_markup=keyboard)

@bot.message_handler(commands=['izoh'])
def handle_izoh_command(message):
    msg = bot.send_message(message.chat.id, "📝 Iltimos, izohingizni yozing:")
    bot.register_next_step_handler(msg, save_user_comment)

from datetime import datetime
import json

def save_user_comment(message):
    user = message.from_user
    izoh_matni = message.text

    try:
        with open("feedback_comments.json", "r", encoding="utf-8") as f:
            comments = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comments = []

    comments.append({
        "user_id": user.id,
        "username": user.username,
        "comment": izoh_matni,
        "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open("feedback_comments.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

    bot.send_message(message.chat.id, "✅ Izohingiz uchun rahmat!")

print("✅ Bot ishga tushdi")
bot.polling(none_stop=True, timeout=20, long_polling_timeout=20)