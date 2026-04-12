import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice
from aiogram.utils import executor

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "510644962"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_lang = {}
user_payment = {}

TEXTS = {
    "ua": {
        "menu": "Оберіть дію 👇",
        "task": "Виконати завдання🙏",
        "tutor": "Потрібен репетитор💪",
        "back": "⬅️ Назад",
        "one": "Одне завдання",
        "complex": "Комплексне виконання роботи",
        "choose": "👇 Обери послугу",
        "pay1": "✅ Оплата 200⭐ пройшла. Надішли файл.",
        "pay2": "✅ Оплата 600⭐ пройшла. Надішли файл.",
        "file": "📩 Файл відправлено адміну",
        "no": "❌ Спочатку оплатіть",
        "tutor_reply": "💪 Напиши, який саме репетитор тобі потрібен"
    },
    "en": {
        "menu": "Choose action 👇",
        "task": "Do task🙏",
        "tutor": "Need tutor💪",
        "back": "⬅️ Back",
        "one": "Single task",
        "complex": "Complex work",
        "choose": "👇 Choose service",
        "pay1": "✅ Paid 200⭐. Send file.",
        "pay2": "✅ Paid 600⭐. Send file.",
        "file": "📩 File sent",
        "no": "❌ Pay first",
        "tutor_reply": "💪 Describe what tutor you need"
    }
}

LANG_MAP = {
    "Українська": "ua",
    "English": "en",
    "Русский": "ru",
    "Suomi": "fi"
}

def lang_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Українська","English")
    kb.row("Русский","Suomi")
    return kb

def main_menu(l):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[l]["task"])
    kb.row(TEXTS[l]["tutor"])
    return kb

def task_menu(l):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[l]["one"])
    kb.row(TEXTS[l]["complex"])
    kb.row(TEXTS[l]["back"])
    return kb

@dp.message_handler(commands=["start"])
async def start(m: types.Message):
    await m.answer(
        "👋Вибери мову бота\n"
        "👋 Select the bot language\n"
        "👋 Выберите язык бота\n"
        "👋 Valitse botin kieli",
        reply_markup=lang_kb()
    )

@dp.message_handler(lambda m: m.text in LANG_MAP)
async def set_lang(m: types.Message):
    l = LANG_MAP[m.text]
    user_lang[m.from_user.id] = l
    await m.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))

@dp.pre_checkout_query_handler(lambda q: True)
async def pc(q):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def paid(m: types.Message):
    l = user_lang.get(m.from_user.id,"ua")
    p = m.successful_payment.invoice_payload

    if p == "t":
        user_payment[m.from_user.id] = "t"
        await m.answer(TEXTS[l]["pay1"])

    elif p == "c":
        user_payment[m.from_user.id] = "c"
        await m.answer(TEXTS[l]["pay2"])

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def file(m: types.Message):
    l = user_lang.get(m.from_user.id,"ua")

    if m.from_user.id not in user_payment:
        await m.answer(TEXTS[l]["no"])
        return

    await bot.send_document(OWNER_ID, m.document.file_id)
    await m.answer(TEXTS[l]["file"])

    del user_payment[m.from_user.id]

@dp.message_handler()
async def menu(m: types.Message):
    l = user_lang.get(m.from_user.id, "ua")

    if m.text == TEXTS[l]["task"]:
        await m.answer(TEXTS[l]["choose"], reply_markup=task_menu(l))

    elif m.text == TEXTS[l]["back"]:
        await m.answer(TEXTS[l]["menu"], reply_markup=main_menu(l))

    elif m.text == TEXTS[l]["tutor"]:
        await m.answer(TEXTS[l]["tutor_reply"], reply_markup=main_menu(l))

    elif m.text == TEXTS[l]["one"]:
        await bot.send_invoice(
            m.chat.id,
            "Task",
            "Single",
            "t",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("Task", 200)],
            start_parameter="t"
        )

    elif m.text == TEXTS[l]["complex"]:
        await bot.send_invoice(
            m.chat.id,
            "Complex",
            "Full",
            "c",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("Complex", 600)],
            start_parameter="c"
        )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)