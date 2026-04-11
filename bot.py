import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, PreCheckoutQueryHandler, filters
)
from openai import OpenAI

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
    sub_end TEXT,
    mode TEXT
)
""")

conn.commit()

# ---------------- SUBSCRIPTION ----------------
def is_sub(uid):
    cur.execute("SELECT sub_end FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    if not r or not r[0]:
        return False
    return datetime.fromisoformat(r[0]) > datetime.now()

def set_sub(uid, days):
    end = datetime.now() + timedelta(days=days)
    cur.execute("INSERT OR REPLACE INTO users (user_id, sub_end) VALUES (?,?)",
                (uid, end.isoformat()))
    conn.commit()

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🤖 AI Tutor", callback_data="ai")],
        [InlineKeyboardButton("💰 Buy subscription", callback_data="buy")]
    ]
    await update.message.reply_text("PRO SaaS Bot 🚀", reply_markup=InlineKeyboardMarkup(kb))

# ---------------- CALLBACK ----------------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # BUY MENU
    if q.data == "buy":
        kb = [
            [InlineKeyboardButton("⭐ 100 Stars / 7 days", callback_data="sub_7")],
            [InlineKeyboardButton("⭐ 300 Stars / 30 days", callback_data="sub_30")]
        ]
        await q.message.edit_text("Choose plan:", reply_markup=InlineKeyboardMarkup(kb))

    # REAL STARS PAYMENT
    elif q.data.startswith("sub_"):
        days = int(q.data.split("_")[1])

        await context.bot.send_invoice(
            chat_id=uid,
            title="PRO Access",
            description=f"{days} days subscription",
            payload=f"sub_{days}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("Stars", 100 if days == 7 else 300)]
        )

# ---------------- PRECHECKOUT ----------------
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

# ---------------- SUCCESS PAYMENT ----------------
async def success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    payload = update.message.successful_payment.invoice_payload

    if "sub_7" in payload:
        set_sub(uid, 7)
    elif "sub_30" in payload:
        set_sub(uid, 30)

    await update.message.reply_text("✅ Payment successful! You now have PRO access.")

# ---------------- GPT AI ----------------
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if not is_sub(uid):
        await update.message.reply_text("❌ Buy subscription first")
        return

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": text}
            ]
        )

        await update.message.reply_text(resp.choices[0].message.content)

    except Exception as e:
        await update.message.reply_text("AI error. Check API key.")

# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(PreCheckoutQueryHandler(precheckout))
app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, success))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai))

app.run_polling()