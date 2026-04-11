import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, PreCheckoutQueryHandler

TOKEN = os.getenv("TOKEN")
OWNER_ID = 510644962

# ---------------- DB ----------------
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, lang TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, text TEXT, status TEXT DEFAULT 'new')""")
cur.execute("""CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, status TEXT)""")
conn.commit()

# ---------------- TEXTS ----------------
texts = {
    "ua": {"menu":"Оберіть дію 👇","task":"Виконати завдання🙏","tutor":"Потрібен репетитор💪","one":"Одне завдання ⭐100","complex":"Комплекс ⭐500"},
    "en": {"menu":"Choose action 👇","task":"Do task🙏","tutor":"Need tutor💪","one":"Single task ⭐100","complex":"Full work ⭐500"},
    "ru": {"menu":"Выберите действие 👇","task":"Выполнить🙏","tutor":"Нужен репетитор💪","one":"Одно ⭐100","complex":"Комплекс ⭐500"},
    "fi": {"menu":"Valitse 👇","task":"Tehtävä🙏","tutor":"Tarvitsen tutor💪","one":"Yksi ⭐100","complex":"Koko ⭐500"}
}

def get_lang(uid):
    cur.execute("SELECT lang FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return r[0] if r else "ua"

def set_lang(uid, lang):
    cur.execute("INSERT OR REPLACE INTO users VALUES (?,?)", (uid, lang))
    conn.commit()

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Українська", callback_data="lang_ua"),
         InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Русский", callback_data="lang_ru"),
         InlineKeyboardButton("Suomi", callback_data="lang_fi")]
    ]
    await update.message.reply_text("🌍 Language", reply_markup=InlineKeyboardMarkup(kb))

# ---------------- PAYMENT ----------------
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    lang = get_lang(uid)

    amount = 100 if q.data == "pay_100" else 500

    await context.bot.send_invoice(
        chat_id=uid,
        title="Task payment",
        description="Unlock task",
        payload=f"pay_{amount}",
        provider_token="",  # ⚠️ Stars НЕ потребують provider token
        currency="XTR",
        prices=[LabeledPrice("Stars", amount)]
    )

# ---------------- PRECHECKOUT ----------------
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

# ---------------- SUCCESS ----------------
async def success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    cur.execute("INSERT INTO payments (user_id, amount, status) VALUES (?,?,?)", (uid, 100, "paid"))
    conn.commit()
    await update.message.reply_text("✅ Оплата успішна! Надішліть файл для перевірки.")

# ---------------- CALLBACK ----------------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data.startswith("lang_"):
        lang = q.data.split("_")[1]
        set_lang(uid, lang)

        kb = [
            [InlineKeyboardButton("Виконати завдання🙏", callback_data="task")],
            [InlineKeyboardButton("Потрібен репетитор💪", callback_data="tutor")]
        ]
        await q.message.edit_text(texts[lang]["menu"], reply_markup=InlineKeyboardMarkup(kb))

    elif q.data == "task":
        lang = get_lang(uid)
        kb = [
            [InlineKeyboardButton(texts[lang]["one"], callback_data="pay_100")],
            [InlineKeyboardButton(texts[lang]["complex"], callback_data="pay_500")]
        ]
        await q.message.edit_text("💰 Оплата:", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data == "tutor":
        cur.execute("INSERT INTO requests (user_id, text) VALUES (?,?)", (uid, "tutor"))
        conn.commit()

        if uid == OWNER_ID:
            await q.message.reply_text("Owner request")
        else:
            await context.bot.send_message(OWNER_ID, f"📩 Tutor request: {uid}")

        await q.message.edit_text("✅ Sent")

# ---------------- ADMIN ----------------
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return
    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM requests")
    req = cur.fetchone()[0]

    await update.message.reply_text(f"👑 ADMIN\nUsers: {users}\nRequests: {req}")

# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(CallbackQueryHandler(pay, pattern="pay_"))
app.add_handler(PreCheckoutQueryHandler(precheckout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, success))

app.run_polling()