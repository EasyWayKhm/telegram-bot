import os
import sqlite3
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, PreCheckoutQueryHandler, filters
)

from openai import OpenAI

# ---------------- CONFIG ----------------
TOKEN = os.getenv("TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
OWNER_ID = 510644962

client = OpenAI(api_key=OPENAI_KEY)

# ---------------- DB ----------------
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    sub_end TEXT
)
""")

conn.commit()

# ---------------- SUB SYSTEM ----------------
def is_sub(uid):
    cur.execute("SELECT sub_end FROM users WHERE user_id=?", (uid,))
    row = cur.fetchone()
    if not row or not row[0]:
        return False
    return datetime.fromisoformat(row[0]) > datetime.now()

def set_sub(uid, days):
    end = datetime.now() + timedelta(days=days)
    cur.execute("INSERT OR REPLACE INTO users VALUES (?,?)",
                (uid, end.isoformat()))
    conn.commit()

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🤖 AI Tutor", callback_data="ai")],
        [InlineKeyboardButton("💰 Buy subscription", callback_data="buy")]
    ]
    await update.message.reply_text("🚀 PRO SaaS Bot", reply_markup=InlineKeyboardMarkup(kb))

# ---------------- CALLBACK ----------------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # меню покупки
    if q.data == "buy":
        kb = [
            [InlineKeyboardButton("⭐ 100 Stars / 7 days", callback_data="sub_7")],
            [InlineKeyboardButton("⭐ 300 Stars / 30 days", callback_data="sub_30")]
        ]
        await q.message.edit_text("Choose subscription:", reply_markup=InlineKeyboardMarkup(kb))

    # запуск оплати
    elif q.data.startswith("sub_"):
        days = int(q.data.split("_")[1])
        price = 100 if days == 7 else 300

        await context.bot.send_invoice(
            chat_id=uid,
            title="PRO Subscription",
            description=f"{days} days access",
            payload=f"sub_{days}",
            provider_token="",  # Telegram Stars
            currency="XTR",
            prices=[LabeledPrice("Subscription", price)]
        )

# ---------------- PRECHECKOUT ----------------
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

# ---------------- SUCCESS PAYMENT ----------------
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    payload = update.message.successful_payment.invoice_payload

    if payload == "sub_7":
        set_sub(uid, 7)
    elif payload == "sub_30":
        set_sub(uid, 30)

    await update.message.reply_text("✅ Subscription activated!")

# ---------------- AI ----------------
async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if not is_sub(uid):
        await update.message.reply_text("❌ Buy subscription first")
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": text}
            ]
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception:
        await update.message.reply_text("❌ AI error (check OPENAI_KEY)")

# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

# handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(PreCheckoutQueryHandler(precheckout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler))

# запуск (правильний)
app.run_polling(drop_pending_updates=True)
