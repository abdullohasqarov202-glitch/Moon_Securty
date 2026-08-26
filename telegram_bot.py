import os
from flask import Flask, request
import telebot
from telebot import types

# =========================
# 🔑 TOKEN
# =========================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN topilmadi!")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)

app = Flask(__name__)


# =========================
# 📢 MAJBURIY OBUNA
# =========================

CHANNEL_USERNAME = "@moonsecurityy"
GROUP_USERNAME = "@SENING_GURUHING"


# =========================
# 👤 OBUNANI TEKSHIRISH
# =========================

def check_subscription(user_id):

    channel_ok = False
    group_ok = False

    try:
        member = bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:
            channel_ok = True

    except Exception as e:
        print("Kanal xatosi:", e)

    try:
        member = bot.get_chat_member(
            GROUP_USERNAME,
            user_id
        )

        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:
            group_ok = True

    except Exception as e:
        print("Guruh xatosi:", e)

    return channel_ok and group_ok


# =========================
# 📢 OBUNA TUGMALARI
# =========================

def subscription_keyboard():

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "📢 Kanalga obuna bo‘lish",
            url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "👥 Guruhga qo‘shilish",
            url=f"https://t.me/{GROUP_USERNAME.replace('@', '')}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    )

    return markup


# =========================
# 🎛 4 TA TUGMA
# =========================

def main_keyboard():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "❓ Savol berish",
        "📚 Savollar"
    )

    markup.row(
        "👤 Profilim",
        "ℹ️ Yordam"
    )

    return markup


# =========================
# 🚀 START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id

    if not check_subscription(user_id):

        bot.send_message(
            message.chat.id,

            f"👋 Salom, <b>{message.from_user.first_name}</b>!\n\n"
            "🤖 Savo!\n\n"
            "Botdan foydalanish uchun avval "
            "kanalga a'zo bo‘ling.\n\n"
            "📢 Kanal — majburiy\n"
            "A'zo bo‘lgach, quyidagi tugmani bosing 👇",

            parse_mode="HTML",
            reply_markup=subscription_keyboard()
        )

        return

    bot.send_message(
        message.chat.id,

        f"👋 Salom, <b>{message.from_user.first_name}</b>!\n\n"
        "🤖 Savol-javob botiga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang 👇",

        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# =========================
# ✅ OBUNANI TEKSHIRISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_subscription(call):

    if check_subscription(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )

        bot.send_message(
            call.message.chat.id,

            "🎉 <b>Obuna tasdiqlandi!</b>\n\n"
            "Endi botdan foydalanishingiz mumkin 👇",

            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Avval kanal va guruhga a'zo bo‘ling!",
            show_alert=True
        )


# =========================
# ❓ SAVOL BERISH
# =========================

@bot.message_handler(
    func=lambda message: message.text == "❓ Savol berish"
)
def ask_question(message):

    if not check_subscription(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "🚫 Avval kanal va guruhga a'zo bo‘ling!",
            reply_markup=subscription_keyboard()
        )

        return

    bot.send_message(
        message.chat.id,

        "❓ <b>Savolingizni yozing:</b>\n\n"
        "Savolingizni oddiy matn ko‘rinishida yuboring.",

        parse_mode="HTML"
    )


# =========================
# 📚 SAVOLLAR
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📚 Savollar"
)
def questions(message):

    bot.send_message(
        message.chat.id,

        "📚 <b>Ko‘p beriladigan savollar</b>\n\n"
        "1️⃣ Bot qanday ishlaydi?\n"
        "2️⃣ Savolga qanday javob olaman?\n"
        "3️⃣ Botdan foydalanish bepulmi?\n\n"
        "❓ O‘zingizning savolingiz bo‘lsa "
        "«❓ Savol berish» tugmasini bosing.",

        parse_mode="HTML"
    )


# =========================
# 👤 PROFIL
# =========================

@bot.message_handler(
    func=lambda message: message.text == "👤 Profilim"
)
def profile(message):

    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "Username yo‘q"
    )

    bot.send_message(
        message.chat.id,

        f"👤 <b>Sizning profilingiz</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Ism: {user.first_name}\n"
        f"🔗 Username: {username}",

        parse_mode="HTML"
    )


# =========================
# ℹ️ YORDAM
# =========================

@bot.message_handler(
    func=lambda message: message.text == "ℹ️ Yordam"
)
def help_button(message):

    bot.send_message(
        message.chat.id,

        "ℹ️ <b>Yordam</b>\n\n"
        "❓ Savol berish — botga savol yuborish.\n"
        "📚 Savollar — ko‘p beriladigan savollar.\n"
        "👤 Profilim — profilingizni ko‘rish.\n\n"
        "Botdan foydalanish uchun kanal va guruhga "
        "a'zo bo‘lish talab qilinadi.",

        parse_mode="HTML"
    )


# =========================
# 💬 ODDIY SAVOLLAR
# =========================

@bot.message_handler(
    content_types=["text"]
)
def answer_question(message):

    text = message.text.lower()

    # Tugmalarni bu yerda qayta ishlamaymiz
    if text in [
        "❓ savol berish",
        "📚 savollar",
        "👤 profilim",
        "ℹ️ yordam"
    ]:
        return

    if not check_subscription(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "🚫 Avval kanal va guruhga a'zo bo‘ling!",
            reply_markup=subscription_keyboard()
        )

        return

    # Oddiy avtomatik javoblar
    if "salom" in text:

        answer = (
            "👋 Salom! Sizga qanday yordam bera olaman?"
        )

    elif "yordam" in text:

        answer = (
            "ℹ️ Yordam kerak bo‘lsa, savolingizni "
            "to‘liq yozib yuboring."
        )

    elif "bot" in text:

        answer = (
            "🤖 Men savol-javob botiman. "
            "Savolingizni yozing, imkon qadar yordam beraman."
        )

    else:

        answer = (
            "🤔 Savolingiz qabul qilindi!\n\n"
            "Hozircha avtomatik javoblar tizimi ishlamoqda. "
            "Savolingizga mos javob bazaga qo‘shilmagan."
        )

    bot.send_message(
        message.chat.id,
        answer
    )


# =========================
# 🌐 WEBHOOK
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.get_data().decode("utf-8")

        update = telebot.types.Update.de_json(data)

        bot.process_new_updates([update])

        return "OK", 200

    except Exception as e:

        print("Webhook xatosi:", e)

        return "ERROR", 500


# =========================
# 🌍 HOME
# =========================

@app.route("/")
def home():

    return "🤖 Savol-javob bot ishlayapti!"


# =========================
# ▶️ ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    webhook_url = os.environ.get(
        "WEBHOOK_URL"
    )

    if webhook_url:

        webhook_url = webhook_url.rstrip("/")

        bot.remove_webhook()

        bot.set_webhook(
            url=f"{webhook_url}/webhook"
        )

        print(
            f"✅ Webhook o‘rnatildi: "
            f"{webhook_url}/webhook"
        )

    else:

        print(
            "⚠️ WEBHOOK_URL topilmadi!"
        )

    app.run(
        host="0.0.0.0",
        port=port
    )
