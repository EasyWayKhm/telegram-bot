import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TOKEN")
OWNER_ID = 510644962

# ---------------- DATABASE ----------------
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    lang TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    status TEXT DEFAULT 'new'
)
""")

conn.commit()

# ---------------- LANGS ----------------
texts = {
    "ua": {
        "menu": "Оберіть дію 👇",
        "task": "Виконати завдання🙏",
        "tutor": "Потрібен репетитор💪",
        "one": "Одне завдання",
        "complex": "Комплексне виконання роботи",
        "lang": "Оберіть мову"
    },
    "en": {
        "menu": "Choose action 👇",
        "task": "Do task🙏",
        "tutor": "Need tutor💪",
        "one": "Single task",
        "complex": "Full work",
        "lang": "Select language"
    },
    "ru": {
        "menu": "Выберите действие 👇",
        "task": "Выполнить задание🙏",
        "tutor": "Нужен репетитор💪",
        "one": "Одно задание",
        "complex": "Комплексная работа",
        "lang": "Выберите язык"
    },
    "fi": {
        "menu": "Valitse toiminto 👇",
        "task": "Suorita tehtävä🙏",
        "tutor": "Tarvitsen tutorin💪",
        "one": "Yksi tehtävä",
        "complex": "Koko työ",
        "lang": "Valitse kieli"
    }
}

# ---------------- HELPERS ----------------
def get_lang(user_id):
    cur.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return row[0] if row else "ua"

def set_lang(user_id, lang):
    cur.execute("INSERT OR REPLACE INTO users (user_id, lang) VALUES (?,?)", (user_id, lang))
    conn.commit()

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Українська", callback_data="lang_ua"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Suomi", callback_data="lang_fi")
        ]
    ]

    await update.message.reply_text("🌍 Select language", reply_markup=InlineKeyboardMarkup(keyboard))

# ---------------- CALLBACK ----------------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    data = q.data
    user_id = q.from_user.id

    # language select
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        set_lang(user_id, lang)

        kb = [
            [InlineKeyboardButton(texts[lang]["task"], callback_data="task")],
            [InlineKeyboardButton(texts[lang]["tutor"], callback_data="tutor")]
        ]

        await q.message.edit_text(texts[lang]["menu"], reply_markup=InlineKeyboardMarkup(kb))

    # task menu
    elif data == "task":
        lang = get_lang(user_id)

        kb = [
            [InlineKeyboardButton(texts[lang]["one"], callback_data="pay_100")],
            [InlineKeyboardButton(texts[lang]["complex"], callback_data="pay_500")]
        ]

        await q.message.edit_text("💰 Payment options:", reply_markup=InlineKeyboardMarkup(kb))

    # tutor request
    elif data == "tutor":
        cur.execute("INSERT INTO requests (user_id, text) VALUES (?,?)",
                    (user_id, "Tutor request"))
        conn.commit()

        if user_id == OWNER_ID:
            await q.message.reply_text("New tutor request (you are owner)")
        else:
            await context.bot.send_message(OWNER_ID, f"📩 New tutor request from {user_id}")

        await q.message.edit_text("✅ Request sent")

# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))

app.run_polling()