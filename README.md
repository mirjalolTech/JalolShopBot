🛍️ Jalol Shop Telegram Bot

Jalol Shop — bu raqamli mahsulotlar (masalan, Telegram yulduzlari, premium, kurslar va boshqalar) savdosi uchun ishlab chiqilgan avtomatlashtirilgan Telegram bot. Bot to‘lov tasdiqlash, buyurtma boshqaruvi, promo kodlar, statistika va boshqa ko‘plab funksiyalarni o‘z ichiga oladi.
📌 Xususiyatlar

    📸 Buyurtma topshirish — foydalanuvchi skrinshot yuborish orqali buyurtma beradi

    ⏱ Flood Control — foydalanuvchilar noto‘g‘ri yoki ko‘p martalab buyurtma yuborishini cheklaydi

    ✅ Admin Tasdiqlash — admin buyurtmani ko‘rib chiqadi va tasdiqlaydi yoki rad etadi

    💬 Fikr-mulohaza — foydalanuvchilar adminlarga murojaat qila oladi

    🔐 Ban tizimi — noto‘g‘ri xatti-harakatlar uchun foydalanuvchini bloklash imkoniyati

    🎟 Promo kodlar — chegirmali kodlar orqali narxni kamaytirish

    📊 Statistika — buyurtmalar va foydalanuvchilar statistikasi

    📢 Broadcast — barcha foydalanuvchilarga xabar yuborish funksiyasi

    🛒 Mahsulotlar boshqaruvi — admin mahsulot qo‘shishi, o‘chirishi yoki tahrirlashi mumkin

⚙️ Texnologiyalar

    Python 3.10+

    Aiogram 3.x

    SQLite (yoki PostgreSQL, tanlovga qarab)

    Telegram Bot API

🧾 O‘rnatish

    Repositoriyani klon qiling:

git clone https://github.com/username/jalol-shop-bot.git
cd jalol-shop-bot

Virtual muhitni yarating va faollashtiring:

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

Kerakli kutubxonalarni o‘rnating:

pip install -r requirements.txt

.env faylini yarating va quyidagilarni joylashtiring:

BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789
CHANNEL_USERNAME=@JalolShopOfficial

Botni ishga tushiring:

    python main.py

📂 Loyihaning Tuzilishi

jalol_shop/
│
├── main.py               # Botni ishga tushirish
├── data/                 # Baza va fayllar
├── config.py             # Sozlamalar
└── README.md             # Ushbu fayl

🧑‍💻 Admin Panel

    /adminpanel buyrug‘i orqali kiriladi

    Mahsulot qo‘shish/o‘chirish

    Buyurtmalarni ko‘rish va tasdiqlash

    Promo kodlar yaratish va tahrirlash

    Foydalanuvchilarni ban qilish

📬 Aloqa

    Telegram: @JalolShopOfficial

📝 Litsenziya

Ushbu loyiha ochiq manba sifatida taqdim etiladi. Talablarga mos holda foydalaning va xatoliklarni GitHub orqali xabar bering.
