from collections import defaultdict
postlar = defaultdict(list)
import telebot
from telebot import types
import time
import os
import json

# Railway uchun DATA_DIR va data_path funksiyasi
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
def data_path(filename):
    return os.path.join(DATA_DIR, filename)

# Fayl yo‘llarini Railway uchun moslash
def init_json_file(filename):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

init_json_file(data_path("feedback_comments.json"))

def yukla_mahsulotlar():
    try:
        with open(data_path("products.json"), "r", encoding="utf-8") as file:
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
        with open(data_path("feedback_comments.json"), "r", encoding="utf-8") as f:
            all_comments = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_comments = []

    all_comments.append(izoh)

    with open(data_path("feedback_comments.json"), "w", encoding="utf-8") as f:
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
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    for log in reversed(logs):
        if log["user_id"] == user_id:
            log["status"] = yangi_status
            break

    with open(data_path("buyurtmalar_log.json"), "w", encoding="utf-8") as file:
        json.dump(logs, file, ensure_ascii=False, indent=4)

def feedback_buttons():
    markup = types.InlineKeyboardMarkup()
    for i in range(1, 6):
        markup.add(types.InlineKeyboardButton("⭐️" * i, callback_data=f"feedback_{i}"))
    return markup

def mahsulotlar_menusi():
    markup = types.InlineKeyboardMarkup(row_width=2)
    mahsulotlar = yukla_mahsulotlar().get("stars", {})

    tugmalar = []
    for nom, narx in mahsulotlar.items():
        tugma = types.InlineKeyboardButton(f"{nom} – {narx}", callback_data=nom)
        tugmalar.append(tugma)

    markup.add(*tugmalar)
    return markup


def premium_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    mahsulotlar = yukla_mahsulotlar().get("premium", {})

    tugmalar = []
    for nom, narx in mahsulotlar.items():
        tugma = types.InlineKeyboardButton(f"{nom} – {narx}", callback_data=nom)
        tugmalar.append(tugma)

    markup.add(*tugmalar)
    return markup

def is_banned(user_id, username):
    import json
    try:
        with open(data_path("banned_users.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return False

    return user_id in data["user_ids"] or (username and username in data["usernames"])

# Foydalanuvchi harakati logi va xatolik monitoringi
import traceback

def log_activity(user_id, action, info=None):
    try:
        # Avval eski loglarni o'qib olamiz
        try:
            with open(data_path("activity_log.json"), "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        # Yangi log obyektini qo'shamiz
        logs.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "action": action,
            "info": info or ""
        })
        with open(data_path("activity_log.json"), "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
    except Exception as e:
        pass

ADMIN_ID = 5092720090

def notify_admin_on_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            user_id = args[0].from_user.id if args and hasattr(args[0], 'from_user') else 'Nomaʼlum'
            bot.send_message(ADMIN_ID, f"❗️ Xatolik: {e}\nUser: {user_id}\n{tb}")
            raise
    return wrapper

# Har bir asosiy komandaga log yozish (misol uchun start, referal, promo, buyurtma va h.k.)
# start funksiyasiga misol:
@bot.message_handler(commands=['start'])
@notify_admin_on_error
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or f"id{user_id}"
    log_activity(user_id, 'start', message.text)

    # 🚫 Ban qilingan foydalanuvchi
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")

    # REFERAL: referalni aniqlash
    referrer_id = None
    if len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]
        if referrer_id == user_id:
            referrer_id = None  # O'zini o'zi taklif qilolmaydi

    # 👥 Foydalanuvchini ro‘yxatga olish
    users_file = data_path("users.json")
    users = {}
    if os.path.exists(users_file):
        try:
            with open(users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = {}
    is_new = user_id not in users
    if is_new:
        users[user_id] = username
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)

    # REFERAL: yangi user bo'lsa va referrer_id bor bo'lsa, referalga qo'shish
    if is_new and referrer_id and referrer_id in users:
        referrals = load_referrals()
        if referrer_id not in referrals:
            referrals[referrer_id] = {"count": 0, "claimed": []}
        referrals[referrer_id]["count"] += 1
        save_referrals(referrals)

    # 🧾 Menyu
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🟡 Telegram Stars", "🔵 Telegram Premium")
    markup.add("ℹ️ Biz haqimizda", "🆘 Yordam")
    # 👋 Xush kelibsiz xabari
    bot.send_message(
        message.chat.id,
        "👋 Assalomu alaykum, *JalolShop* botiga xush kelibsiz!\n\nXizmat turini tanlang 👇",
        reply_markup=markup,
        parse_mode='Markdown'
    )
    print(f"Foydalanuvchi: {username} ({user_id}) start bosdi.")

@bot.message_handler(commands=['adminpanel'])
def admin_panel(message):
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
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
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    admin_id = 5092720090
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")
        return

    try:
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
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
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    if message.from_user.id != 5092720090:
        return bot.send_message(message.chat.id, "⛔ Siz admin emassiz.")

    try:
        with open(data_path("feedback_log.json"), "r", encoding="utf-8") as f:
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
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    if message.from_user.id != 5092720090:
        return bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")
    
    try:
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
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


@bot.message_handler(commands=['profile'])
def show_profile(message):
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    user_id = message.from_user.id
    try:
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    try:
        with open(data_path("feedback_log.json"), "r", encoding="utf-8") as f:
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

@bot.message_handler(commands=['izohlar'])
def show_comments(message):
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    admin_id = 5092720090

    if message.from_user.id != admin_id:
        return bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")

    try:
        with open(data_path("feedback_comments.json"), "r", encoding="utf-8") as f:
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
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append(log_entry)

    with open(data_path("buyurtmalar_log.json"), "w", encoding="utf-8") as file:
        json.dump(logs, file, ensure_ascii=False, indent=4)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    user = message.from_user
    user_id = user.id

    try:
        with open(data_path("cooldowns.json"), "r", encoding="utf-8") as f:
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
        bot.reply_to(message, "⚠️ Siz allaqoncha chek yuborgansiz. Iltimos, admin tasdiqlaguncha kuting.")
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
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
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
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
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
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")

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
            with open(data_path("cooldowns.json"), "r", encoding="utf-8") as f:
                cooldowns = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cooldowns = {}

        cooldowns[str(user_id)] = time.time() + 120  # 2 daqiqa

        with open(data_path("cooldowns.json"), "w", encoding="utf-8") as f:
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
            with open(data_path("cooldowns.json"), "r", encoding="utf-8") as f:
                cooldowns = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cooldowns = {}

        cooldowns[str(user_id)] = time.time() + 1800  # 30 daqiqa

        with open(data_path("cooldowns.json"), "w", encoding="utf-8") as f:
            json.dump(cooldowns, f, indent=4)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def mahsulot_kiritish_bosqichi(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")

    if call.from_user.id != 5092720090:
        return

    kategoriya = call.data.split("_")[1]

    msg = bot.send_message(
        call.message.chat.id,
        f"➕ Yangi mahsulotni {kategoriya} bo‘limiga kiriting:\n\nFormat: Nomi - Narxi",
        parse_mode="Markdown"
    )

    bot.register_next_step_handler(msg, lambda m: saqlash_mahsulot(m, kategoriya))

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def mahsulot_kiritish_bosqichi(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")

    if call.from_user.id != 5092720090:
        return

    kategoriya = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, f"➕ Yangi mahsulotni {kategoriya} bo‘limiga kiriting:\n\nFormat: Nomi - Narxi", parse_mode="Markdown")
    
    bot.register_next_step_handler(msg, lambda m: saqlash_mahsulot(m, kategoriya))


@bot.callback_query_handler(func=lambda call: call.data == "admin_add_product")
def admin_add_product(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")

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
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    
    if call.from_user.id != 5092720090:
        return

    mahsulotlar = yukla_mahsulotlar()
    tugmalar = types.InlineKeyboardMarkup()

    for kategoriya, items in mahsulotlar.items():
        for nom in items:
            tugmalar.add(
                types.InlineKeyboardButton(
                    text=f"{nom}", 
                    callback_data=f"delete_{kategoriya}_{nom}"
                )
            )

    bot.send_message(
        call.message.chat.id, 
        "🗑 O‘chirish uchun mahsulotni tanlang:", 
        reply_markup=tugmalar
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def mahsulot_ni_ochir(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    
    if call.from_user.id != 5092720090:
        return

    _, kategoriya, nom = call.data.split("_", 2)
    mahsulotlar = yukla_mahsulotlar()

    if kategoriya in mahsulotlar and nom in mahsulotlar[kategoriya]:
        del mahsulotlar[kategoriya][nom]

        with open(data_path("products.json"), "w", encoding="utf-8") as file:
            json.dump(mahsulotlar, file, ensure_ascii=False, indent=4)

        bot.answer_callback_query(call.id, f"✅ '{nom}' o‘chirildi.")
        bot.edit_message_text("✅ Mahsulot muvaffaqiyatli o‘chirildi.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Mahsulot topilmadi.")

@bot.callback_query_handler(func=lambda call: call.data == "admin_export_excel")
def handle_export_excel(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    export_log(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "admin_clean_logs")
def handle_clean_logs(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    admin_id = 5092720090

    try:
        with open(data_path("buyurtmalar_log.json"), "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
        bot.send_message(admin_id, "🧹 Eski buyurtma loglari tozalandi.")
    except Exception as e:
        bot.send_message(admin_id, f"❗️ Log faylni tozalashda xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_grafik")
def send_graph(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
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
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    if call.from_user.id != 5092720090:
        return
    msg = bot.send_message(call.message.chat.id, "📣 Reklama matnini yuboring:")
    bot.register_next_step_handler(msg, process_broadcast)

@bot.callback_query_handler(func=lambda call: call.data.startswith("feedback_"))
def handle_feedback(call):
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
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
        with open(data_path("feedback_log.json"), "r", encoding="utf-8") as f:
            feedbacklar = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        feedbacklar = []

    feedbacklar.append(feedback)

    with open(data_path("feedback_log.json"), "w", encoding="utf-8") as f:
        json.dump(feedbacklar, f, ensure_ascii=False, indent=4)

    admin_id = 5092720090
    bot.send_message(admin_id, f"📝 @{call.from_user.username} {baho} ⭐️ baho berdi.")

def process_broadcast(message):
    try:
        with open(data_path("users.json"), "r", encoding="utf-8") as file:
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
    if is_banned(call.from_user.id, call.from_user.username):
        return bot.send_message(call.message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
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

    with open(data_path("products.json"), "w", encoding="utf-8") as file:
        json.dump(mahsulotlar, file, ensure_ascii=False, indent=4)

    bot.send_message(message.chat.id, f"✅ Mahsulot qo‘shildi:\n\n<b>{nom}</b> – <b>{narx}</b>", parse_mode='HTML')


@bot.message_handler(commands=['status'])
def check_status(message):
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    user_id = message.from_user.id
    try:
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
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
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    admin_id = 5092720090
    if message.from_user.id != admin_id:
        bot.send_message(message.chat.id, "⛔ Siz admin emassiz.")
        return

    try:
        with open(data_path("buyurtmalar_log.json"), "r", encoding="utf-8") as file:
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
    if is_banned(message.from_user.id, message.from_user.username):
        return bot.send_message(message.chat.id, "🚫 Siz admin tomonidan bloklangansiz.")
    msg = bot.send_message(message.chat.id, "📝 Iltimos, izohingizni yozing:")
    bot.register_next_step_handler(msg, save_user_comment)

from datetime import datetime
import json

def save_user_comment(message):
    user = message.from_user
    izoh_matni = message.text

    try:
        with open(data_path("feedback_comments.json"), "r", encoding="utf-8") as f:
            comments = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comments = []

    comment_obj = {
        "user_id": user.id,
        "username": user.username,
        "comment": izoh_matni,
        "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    comments.append(comment_obj)

    with open(data_path("feedback_comments.json"), "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

    bot.send_message(message.chat.id, "✅ Izohingiz uchun rahmat!")

    # Admin ID ga izohni yuborish
    admin_id = 5092720090
    matn = (
        f"📝 <b>Yangi izoh!</b>\n"
        f"👤 <b>@{user.username or 'no_username'}</b>\n"
        f"💬 {izoh_matni}\n"
        f"🕒 {comment_obj['vaqt']}\n"
    )
    bot.send_message(admin_id, matn, parse_mode='HTML')

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != 5092720090:
        return
    args = message.text.split()
    if len(args) < 2:
        return bot.send_message(message.chat.id, "⚠️ /ban 123456789 yoki /ban @username")

    try:
        with open(data_path("banned_users.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"user_ids": [], "usernames": []}

    target = args[1]
    if target.startswith("@"):
        if target[1:] not in data["usernames"]:
            data["usernames"].append(target[1:])
    else:
        uid = int(target)
        if uid not in data["user_ids"]:
            data["user_ids"].append(uid)

    with open(data_path("banned_users.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    bot.send_message(message.chat.id, "✅ Foydalanuvchi bloklandi.")


@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id != 5092720090:
        return
    args = message.text.split()
    if len(args) < 2:
        return bot.send_message(message.chat.id, "⚠️ /unban 123456789 yoki /unban @username")

    try:
        with open(data_path("banned_users.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return bot.send_message(message.chat.id, "⚠️ Ban fayli topilmadi.")

    target = args[1]
    if target.startswith("@"):
        if target[1:] in data["usernames"]:
            data["usernames"].remove(target[1:])
    else:
        uid = int(target)
        if uid in data["user_ids"]:
            data["user_ids"].remove(uid)

    with open(data_path("banned_users.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    bot.send_message(message.chat.id, "✅ Foydalanuvchi ban’dan chiqarildi.")

@bot.message_handler(func=lambda message: message.text == "🟡 Telegram Stars")
@notify_admin_on_error
def show_stars(message):
    mahsulotlar = yukla_mahsulotlar().get("stars", {})
    if not mahsulotlar:
        return bot.send_message(message.chat.id, "❗️ Hozircha Telegram Stars mahsulotlari mavjud emas.")
    matn = "<b>🟡 Telegram Stars narxlari:</b>\n" "Buyurtma uchun mahsulotni tanlang va to‘lov screenshotini yuboring."
    bot.send_message(message.chat.id, matn, parse_mode='HTML', reply_markup=mahsulotlar_menusi())

@bot.message_handler(func=lambda message: message.text == "🔵 Telegram Premium")
@notify_admin_on_error
def show_premium(message):
    mahsulotlar = yukla_mahsulotlar().get("premium", {})

    if not mahsulotlar:
        return bot.send_message(message.chat.id, "❗️ Hozircha Telegram Premium mahsulotlari mavjud emas.")

    matn = "<b>🔵 Telegram Premium narxlari:</b>\n" "Buyurtma uchun mahsulotni tanlang va to‘lov screenshotini yuboring."
    bot.send_message(message.chat.id, matn, parse_mode='HTML', reply_markup=premium_menu())

@bot.message_handler(func=lambda message: message.text == "ℹ️ Biz haqimizda")
@notify_admin_on_error
def about_us(message):
    matn = (
        "ℹ️ <b>Biz haqimizda</b>\n\n"
        "JalolShop — ishonchli va tezkor Telegram Stars va Premium xizmatlari do‘koni.\n"
        "\nBarcha mahsulotlar rasmiy va kafolatlangan.\n"
        "\nSavollar uchun: @jaloI_admin"
    )
    bot.send_message(message.chat.id, matn, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "🆘 Yordam")
@notify_admin_on_error
def help_menu(message):
    matn = (
        "🆘 <b>Yordam</b>\n\n"
        "1. Mahsulot tanlang va to‘lovni amalga oshiring.\n"
        "2. To‘lov screenshotini yuboring.\n"
        "3. Ko'p so'raladigan savollar /faq \n"
        "4. Admin tasdiqlaganidan so‘ng mahsulotni olasiz.\n"
        "\nSavollar uchun: @jaloI_admin \n"
    )
    bot.send_message(message.chat.id, matn, parse_mode='HTML')

@bot.message_handler(commands=['faq'])
@notify_admin_on_error
def faq(message):
    matn = (
        "<b>Tez-tez so'raladigan savollar (FAQ)</b>\n\n"
        "<b>1. Qanday to'lov qilish mumkin?</b>\n"
        "- Mahsulotni tanlang, narxini ko'ring va to'lovni karta raqamiga amalga oshiring.\n"
        "- To'lovdan so'ng screenshotni botga yuboring.\n\n"
        "<b>2. To'lovdan keyin mahsulotni qachon olaman?</b>\n"
        "- Admin to'lovni tekshiradi va mahsulotingizni tez orada yetkazib beradi.\n\n"
        "<b>3. Qanday kartalarga to'lov qilinadi?</b>\n"
        "- Uzcard va Humo kartalariga to'lov qabul qilinadi.\n\n"
        "<b>4. Muammo yoki savol bo'lsa kimga murojaat qilaman?</b>\n"
        "- @jaloI_admin ga yozing yoki '🆘 Yordam' tugmasidan foydalaning.\n\n"
        "<b>5. Botdan qanday foydalanaman?</b>\n"
        "- Quyidagi video yo'riqnoma orqali to'liq ko'rishingiz mumkin:\n"
        "👉 <a href='https://t.me/JalolShopOfficial/117'>Botdan foydalanish videosi</a>\n\n"
        "Boshqa savollar uchun admin bilan bog'laning!"
    )
    bot.send_message(message.chat.id, matn, parse_mode='HTML', disable_web_page_preview=True)

# --- REFERAL SYSTEM START ---
def load_referrals():
    try:
        with open(data_path("referrals.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_referrals(data):
    with open(data_path("referrals.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
# --- REFERAL SYSTEM END ---

@bot.message_handler(commands=['referal'])
def referal_info(message):
    user_id = str(message.from_user.id)
    referrals = load_referrals()
    count = referrals.get(user_id, {}).get("count", 0)
    claimed = referrals.get(user_id, {}).get("claimed", [])
    mahsulotlar = yukla_mahsulotlar().get("stars", {})
    # Faqat raqamli nomlarni olamiz (50, 75, 100...)
    available = [int(nom.split()[0]) for nom in mahsulotlar.keys() if nom.split()[0].isdigit()]
    available.sort()
    # Qancha miqdorlarni yechib olishi mumkin
    withdrawable = [x for x in available if x <= count and x not in claimed]
    # Referal havola
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    matn = (
        f"🔗 <b>Sizning referal havolangiz:</b>\n<code>{link}</code>\n\n"
        f"👥 Taklif qilgan referallaringiz soni: <b>{count}</b>\n"
        f"🎁 Sovg'a olish uchun quyidagilardan birini tanlang:\n"
    )
    markup = types.InlineKeyboardMarkup()
    for x in withdrawable:
        tugma = types.InlineKeyboardButton(f"{x} ta Stars (olish)", callback_data=f"referal_withdraw_{x}")
        markup.add(tugma)
    if not withdrawable:
        matn += "<i>Hozircha sovg'a olish uchun yetarli referal yo'q yoki hammasi olingan.</i>"
    bot.send_message(message.chat.id, matn, parse_mode='HTML', reply_markup=markup if withdrawable else None)

@bot.callback_query_handler(func=lambda call: call.data.startswith("referal_withdraw_"))
def referal_withdraw(call):
    user_id = str(call.from_user.id)
    referrals = load_referrals()
    count = referrals.get(user_id, {}).get("count", 0)
    claimed = referrals.get(user_id, {}).get("claimed", [])
    mahsulotlar = yukla_mahsulotlar().get("stars", {})
    available = [int(nom.split()[0]) for nom in mahsulotlar.keys() if nom.split()[0].isdigit()]
    available.sort()
    x = int(call.data.split("_")[-1])
    if x not in available or x > count or x in claimed:
        bot.answer_callback_query(call.id, "❌ Bu miqdorni yechib bo'lmaydi!", show_alert=True)
        return
    # Sovg'a berish (admin xabar oladi)
    referrals.setdefault(user_id, {"count": 0, "claimed": []})
    referrals[user_id]["claimed"].append(x)
    save_referrals(referrals)
    # Foydalanuvchiga xabar
    bot.send_message(user_id, f"🎉 Tabriklaymiz! Siz {x} ta Stars sovg'asini oldingiz! Admin tez orada sizga yetkazib beradi.")
    # Admin xabari
    admin_id = 5092720090
    bot.send_message(admin_id, f"🎁 @{call.from_user.username or user_id} {x} ta Stars referal sovg'asini oldi!")
    bot.answer_callback_query(call.id, "✅ So'rovingiz qabul qilindi!", show_alert=True)

@bot.message_handler(commands=['referalstats'])
def referal_stats(message):
    if message.from_user.id != 5092720090:
        return bot.send_message(message.chat.id, "⛔️ Siz admin emassiz.")
    referrals = load_referrals()
    users_file = data_path("users.json")
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = {}
    # Top 5 userlar
    top = sorted(referrals.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:5]
    if not top:
        return bot.send_message(message.chat.id, "❗️ Hali hech kimda referal yo'q.")
    text = "<b>🏆 TOP 5 referalchilar:</b>\n\n"
    for i, (uid, info) in enumerate(top, 1):
        username = users.get(uid, f"id{uid}")
        text += f"{i}. @{username} — {info.get('count', 0)} ta referal\n"
    bot.send_message(message.chat.id, text, parse_mode='HTML')
    
print("✅ Bot ishga tushdi")
bot.polling(none_stop=True, timeout=20, long_polling_timeout=20)