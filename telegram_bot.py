import logging
import os
 
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)
 
# ---------------------------------------------------------------------------
# Sozlamalar (.env fayldan olinadi)
# ---------------------------------------------------------------------------
load_dotenv()
 
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # masalan: @mening_kanalim
CHANNEL_ID = os.getenv("CHANNEL_ID")  # masalan: -1001234567890 (username ishlamasa shu ishlatiladi)
 
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
 
 
# ---------------------------------------------------------------------------
# Yordamchi funksiyalar
# ---------------------------------------------------------------------------
def get_subscribe_keyboard() -> InlineKeyboardMarkup:
    """Obuna bo'lish va tekshirish tugmalari."""
    channel_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
    keyboard = [
        [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=channel_link)],
        [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")],
    ]
    return InlineKeyboardMarkup(keyboard)
 
 
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Obuna tasdiqlangandan keyin chiqadigan 4 ta tugma (2x2)."""
    keyboard = [
        [
            InlineKeyboardButton("1️⃣ Tugma 1", callback_data="btn_1"),
            InlineKeyboardButton("2️⃣ Tugma 2", callback_data="btn_2"),
        ],
        [
            InlineKeyboardButton("3️⃣ Tugma 3", callback_data="btn_3"),
            InlineKeyboardButton("4️⃣ Tugma 4", callback_data="btn_4"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
 
 
async def is_user_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganini tekshiradi."""
    chat_ref = CHANNEL_ID if CHANNEL_ID else CHANNEL_USERNAME
    try:
        member = await context.bot.get_chat_member(chat_id=chat_ref, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning("Obunani tekshirishda xatolik: %s", e)
        return False
 
 
# ---------------------------------------------------------------------------
# Handlerlar
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    subscribed = await is_user_subscribed(context, user.id)
 
    if subscribed:
        await update.message.reply_text(
            f"Salom, {user.first_name}! 👋\n\nQuyidagi menyudan birini tanlang:",
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await update.message.reply_text(
            f"Salom, {user.first_name}! 👋\n\n"
            "Botdan foydalanish uchun avval kanalimizga obuna bo'lishingiz kerak.\n"
            "Obuna bo'lgach, pastdagi \"Obunani tekshirish\" tugmasini bosing.",
            reply_markup=get_subscribe_keyboard(),
        )
 
 
async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    subscribed = await is_user_subscribed(context, user.id)
 
    if subscribed:
        await query.answer("Obuna tasdiqlandi ✅")
        await query.edit_message_text(
            f"Rahmat, {user.first_name}! Endi botdan to'liq foydalanishingiz mumkin.\n\n"
            "Quyidagi menyudan birini tanlang:",
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await query.answer("Siz hali kanalga obuna bo'lmagansiz ❌", show_alert=True)
 
 
async def menu_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """4 ta menyu tugmasi bosilganda ishlaydi."""
    query = update.callback_query
    await query.answer()
 
    responses = {
        "btn_1": "Siz 1-tugmani bosdingiz.",
        "btn_2": "Siz 2-tugmani bosdingiz.",
        "btn_3": "Siz 3-tugmani bosdingiz.",
        "btn_4": "Siz 4-tugmani bosdingiz.",
    }
    text = responses.get(query.data, "Noma'lum buyruq.")
 
    await query.edit_message_text(
        text=text,
        reply_markup=get_main_menu_keyboard(),
    )
 
 
# ---------------------------------------------------------------------------
# Botni ishga tushirish
# ---------------------------------------------------------------------------
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylga BOT_TOKEN qo'shing.")
    if not CHANNEL_USERNAME and not CHANNEL_ID:
        raise RuntimeError("CHANNEL_USERNAME yoki CHANNEL_ID .env faylda ko'rsatilishi kerak.")
 
    app = Application.builder().token(BOT_TOKEN).build()
 
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(menu_button_callback, pattern="^btn_"))
 
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
 
 
if __name__ == "__main__":
    main()
 
