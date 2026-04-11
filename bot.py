import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("TOKEN")

# 🔹 Тексти
TEXTS = {
    "ua": "Привіт! Обери дію 👇",
    "en": "Hello! Choose action 👇",
    "ru": "Привет! Выберите действие 👇",
    "fi": "Hei! Valitse toiminto 👇"
}

# 🔹 Мови користувачів (простий варіант)
user_lang = {}

# 🔹 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Українська", callback_data="lang_ua"),
            InlineKeyboardButton("English", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Suomi", callback_data="lang_fi"),
        ]
    ]

    text = (
        "Вітаю! 👋\n"
        "Choose language / Оберіть мову"
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔹 вибір мови
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[1]
    user_lang[query.from_user.id] = lang

    await query.message.edit_text(TEXTS[lang])

# 🔹 запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(set_language, pattern="lang_"))

app.run_polling()