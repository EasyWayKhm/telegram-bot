import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice
from aiogram.utils import executor

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "510644962"))

if not API_TOKEN:
    raise ValueError("API_TOKEN not found. Add it to .env or Railway Variables.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_lang = {}
user_payment = {}

TEXTS = {
    "ua": {
        "select_language": (
            "Вітаю з підпискою! 👋\n\n"
            "Вибери мову бота\n"
            "Congratulations on subscribing! 👋\n"
            "Select the bot language\n"
            "Поздравляем с подпиской! 👋\n"
            "Выберите язык бота\n"
            "Onnittelut tilauksestasi! 👋\n"
            "Valitse botin kieli"
        ),
        "menu": "Оберіть дію 👇",
        "task": "Виконати завдання🙏",
        "tutor": "Потрібен репетитор💪",
        "change_language": "Змінити мову🌍",
        "one": "Одне завдання",
        "complex": "Комплексне виконання роботи",
        "choose_service": "👇 Обери послугу",
        "pay_success_task": "✅ Оплата за одне завдання пройшла успішно. Надішли файл.",
        "pay_success_complex": "✅ Оплата за комплексне виконання роботи пройшла успішно. Надішли файл.",
        "file_sent": "📩 Файл відправлено адміністратору.",
        "no_payment": "❌ Спочатку потрібно оплатити.",
        "tutor_reply": "💪 Напиши, який саме репетитор тобі потрібен, і адміністратор зв’яжеться з тобою."
    },
    "en": {
        "select_language": (
            "Вітаю з підпискою! 👋\n\n"
            "Вибери мову бота\n"
            "Congratulations on subscribing! 👋\n"
            "Select the bot language\n"
            "Поздравляем с подпиской! 👋\n"
            "Выберите язык бота\n"
            "Onnittelut tilauksestasi! 👋\n"
            "Valitse botin kieli"
        ),
        "menu": "Choose an action 👇",
        "task": "Do the task🙏",
        "tutor": "Need a tutor💪",
        "change_language": "Change language🌍",
        "one": "Single task",
        "complex": "Complex work",
        "choose_service": "👇 Choose a service",
        "pay_success_task": "✅ Payment for a single task was successful. Send your file.",
        "pay_success_complex": "✅ Payment for complex work was successful. Send your file.",
        "file_sent": "📩 File sent to the administrator.",
        "no_payment": "❌ You must pay first.",
        "tutor_reply": "💪 Tell us what kind of tutor you need, and the administrator will contact you."
    },
    "ru": {
        "select_language": (
            "Вітаю з підпискою! 👋\n\n"
            "Вибери мову бота\n"
            "Congratulations on subscribing! 👋\n"
            "Select the bot language\n"
            "Поздравляем с подпиской! 👋\n"
            "Выберите язык бота\n"
            "Onnittelut tilauksestasi! 👋\n"
            "Valitse botin kieli"
        ),
        "menu": "Выберите действие 👇",
        "task": "Выполнить задание🙏",
        "tutor": "Нужен репетитор💪",
        "change_language": "Сменить язык🌍",
        "one": "Одно задание",
        "complex": "Комплексная работа",
        "choose_service": "👇 Выберите услугу",
        "pay_success_task": "✅ Оплата за одно задание прошла успешно. Отправьте файл.",
        "pay_success_complex": "✅ Оплата за комплексную работу прошла успешно. Отправьте файл.",
        "file_sent": "📩 Файл отправлен администратору.",
        "no_payment": "❌ Сначала нужно оплатить.",
        "tutor_reply": "💪 Напишите, какой именно репетитор вам нужен, и администратор свяжется с вами."
    },
    "fi": {
        "select_language": (
            "Вітаю з підпискою! 👋\n\n"
            "Вибери мову бота\n"
            "Congratulations on subscribing! 👋\n"
            "Select the bot language\n"
            "Поздравляем с подпиской! 👋\n"
            "Выберите язык бота\n"
            "Onnittelut tilauksestasi! 👋\n"
            "Valitse botin kieli"
        ),
        "menu": "Valitse toiminto 👇",
        "task": "Suorita tehtävä🙏",
        "tutor": "Tarvitsetko opettajan💪",
        "change_language": "Vaihda kieli🌍",
        "one": "Yksi tehtävä",
        "complex": "Laajempi työ",
        "choose_service": "👇 Valitse palvelu",
        "pay_success_task": "✅ Maksu yhdestä tehtävästä onnistui. Lähetä tiedosto.",
        "pay_success_complex": "✅ Maksu laajemmasta työstä onnistui. Lähetä tiedosto.",
        "file_sent": "📩 Tiedosto lähetettiin ylläpitäjälle.",
        "no_payment": "❌ Sinun täytyy maksaa ensin.",
        "tutor_reply": "💪 Kerro, millaisen opettajan tarvitset, niin ylläpitäjä ottaa sinuun yhteyttä."
    }
}

LANG_MAP = {
    "Українська": "ua",
    "English": "en",
    "Русский": "ru",
    "Suomi": "fi"
}


def detect_user_language(language_code: str):
    if not language_code:
        return None

    code = language_code.lower()

    if code.startswith("uk"):
        return "ua"
    if code.startswith("en"):
        return "en"
    if code.startswith("ru"):
        return "ru"
    if code.startswith("fi"):
        return "fi"

    return None


def get_language_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(KeyboardButton("Українська"), KeyboardButton("English"))
    kb.row(KeyboardButton("Русский"), KeyboardButton("Suomi"))
    return kb


def get_main_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["task"])
    kb.row(TEXTS[lang]["tutor"])
    kb.row(TEXTS[lang]["change_language"])
    return kb


def get_task_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["one"])
    kb.row(TEXTS[lang]["complex"])
    kb.row(TEXTS[lang]["change_language"])
    return kb


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    detected_lang = detect_user_language(message.from_user.language_code)

    if detected_lang:
        user_lang[message.from_user.id] = detected_lang
        await message.answer(
            TEXTS[detected_lang]["menu"],
            reply_markup=get_main_menu(detected_lang)
        )
        return

    await message.answer(
        TEXTS["ua"]["select_language"],
        reply_markup=get_language_keyboard()
    )


@dp.message_handler(lambda m: m.text in LANG_MAP)
async def set_language(message: types.Message):
    lang = LANG_MAP[message.text]
    user_lang[message.from_user.id] = lang

    await message.answer(
        TEXTS[lang]["menu"],
        reply_markup=get_main_menu(lang)
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    lang = user_lang.get(message.from_user.id, "ua")
    payload = message.successful_payment.invoice_payload

    if payload == "task_payment":
        user_payment[message.from_user.id] = "task"
        await message.answer(TEXTS[lang]["pay_success_task"])

    elif payload == "complex_payment":
        user_payment[message.from_user.id] = "complex"
        await message.answer(TEXTS[lang]["pay_success_complex"])


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    lang = user_lang.get(message.from_user.id, "ua")

    if message.from_user.id not in user_payment:
        await message.answer(TEXTS[lang]["no_payment"])
        return

    order_type = user_payment[message.from_user.id]

    caption_lines = [
        f"📥 New order: {order_type}",
        f"User ID: {message.from_user.id}"
    ]

    if message.from_user.username:
        caption_lines.append(f"Username: @{message.from_user.username}")

    caption = "\n".join(caption_lines)

    await bot.send_document(
        chat_id=OWNER_ID,
        document=message.document.file_id,
        caption=caption
    )

    await message.answer(TEXTS[lang]["file_sent"])

    del user_payment[message.from_user.id]


@dp.message_handler()
async def menu(message: types.Message):
    lang = user_lang.get(message.from_user.id)

    if not lang:
        detected_lang = detect_user_language(message.from_user.language_code)

        if detected_lang:
            user_lang[message.from_user.id] = detected_lang
            await message.answer(
                TEXTS[detected_lang]["menu"],
                reply_markup=get_main_menu(detected_lang)
            )
            return

        await message.answer(
            TEXTS["ua"]["select_language"],
            reply_markup=get_language_keyboard()
        )
        return

    if message.text == TEXTS[lang]["change_language"]:
        user_lang.pop(message.from_user.id, None)
        await message.answer(
            TEXTS["ua"]["select_language"],
            reply_markup=get_language_keyboard()
        )

    elif message.text == TEXTS[lang]["task"]:
        await message.answer(
            TEXTS[lang]["choose_service"],
            reply_markup=get_task_menu(lang)
        )

    elif message.text == TEXTS[lang]["tutor"]:
        await message.answer(
            TEXTS[lang]["tutor_reply"],
            reply_markup=get_main_menu(lang)
        )

    elif message.text == TEXTS[lang]["one"]:
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Task Payment",
            description="Single task",
            payload="task_payment",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Task", amount=200)],
            start_parameter="task"
        )

    elif message.text == TEXTS[lang]["complex"]:
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Complex Payment",
            description="Complex work",
            payload="complex_payment",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Complex", amount=600)],
            start_parameter="complex"
        )

    else:
        await message.answer(
            TEXTS[lang]["menu"],
            reply_markup=get_main_menu(lang)
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)