import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    BotCommand,
)

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
user_state = {}

LANG_BUTTONS = {
    "🇺🇦 Українська": "ua",
    "🇬🇧 English": "en",
    "🇰🇿 Қазақ": "kk",
    "🇮🇩 Indonesia": "id",
    "🇲🇾 Malay": "ms",
    "🇪🇸 Español": "es",
    "🇰🇭 ភាសាខ្មែរ": "km",
    "🇵🇱 Polski": "pl",
    "🇮🇹 Italiano": "it",
    "🇵🇹🇧🇷 Portuguesa": "pt",
    "🇺🇿 Oʻzbekcha": "uz",
    "🇷🇺 Русский": "ru",
}

TEXTS = {
    "ua": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Оберіть дію 👇",
        "task": "Виконати завдання🙏",
        "tutor": "Потрібен репетитор💪",
        "menu_btn": "📋 Меню",
        "profile": "👤 Моя анкета",
        "premium": "⭐ Premium",
        "complain": "🚫 Поскаржитися",
        "language": "🌍 Мова",
        "back": "⬅️ Назад",
        "one": "Одне завдання",
        "complex": "Комплексне виконання роботи",
        "choose_service": "👇 Обери послугу",
        "pay_success_task": "✅ Оплата 200⭐ пройшла успішно. Надішли файл.",
        "pay_success_complex": "✅ Оплата 600⭐ пройшла успішно. Надішли файл.",
        "file_sent": "📩 Файл відправлено адміністратору.",
        "no_payment": "❌ Спочатку потрібно оплатити.",
        "tutor_reply": "💪 Напиши, який саме репетитор тобі потрібен.",
        "profile_text": "🧾 Розділ «Моя анкета» в розробці.",
        "premium_text": "💎 Розділ Premium в розробці.",
        "complain_text": "⚠️ Напиши свою скаргу одним повідомленням, і адміністратор її побачить.",
        "complaint_sent": "✅ Скаргу відправлено адміністратору.",
        "send_file_now": "📎 Тепер можеш надіслати файл.",
        "commands": {
            "myprofile": "Моя анкета",
            "premium": "Premium",
            "complaint": "Поскаржитися",
            "language": "Мова",
        },
    },
    "en": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Choose an action 👇",
        "task": "Do the task🙏",
        "tutor": "Need a tutor💪",
        "menu_btn": "📋 Menu",
        "profile": "👤 My profile",
        "premium": "⭐ Premium",
        "complain": "🚫 Complain",
        "language": "🌍 Language",
        "back": "⬅️ Back",
        "one": "Single task",
        "complex": "Complex work",
        "choose_service": "👇 Choose a service",
        "pay_success_task": "✅ Payment of 200⭐ was successful. Send your file.",
        "pay_success_complex": "✅ Payment of 600⭐ was successful. Send your file.",
        "file_sent": "📩 File sent to the administrator.",
        "no_payment": "❌ You need to pay first.",
        "tutor_reply": "💪 Write what kind of tutor you need.",
        "profile_text": "🧾 The 'My profile' section is under development.",
        "premium_text": "💎 The Premium section is under development.",
        "complain_text": "⚠️ Send your complaint in one message, and the administrator will receive it.",
        "complaint_sent": "✅ Complaint sent to the administrator.",
        "send_file_now": "📎 Now you can send your file.",
        "commands": {
            "myprofile": "My profile",
            "premium": "Premium",
            "complaint": "Complain",
            "language": "Language",
        },
    },
    "ru": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Выберите действие 👇",
        "task": "Выполнить задание🙏",
        "tutor": "Нужен репетитор💪",
        "menu_btn": "📋 Меню",
        "profile": "👤 Моя анкета",
        "premium": "⭐ Premium",
        "complain": "🚫 Пожаловаться",
        "language": "🌍 Язык",
        "back": "⬅️ Назад",
        "one": "Одно задание",
        "complex": "Комплексное выполнение работы",
        "choose_service": "👇 Выберите услугу",
        "pay_success_task": "✅ Оплата 200⭐ прошла успешно. Отправьте файл.",
        "pay_success_complex": "✅ Оплата 600⭐ прошла успешно. Отправьте файл.",
        "file_sent": "📩 Файл отправлен администратору.",
        "no_payment": "❌ Сначала нужно оплатить.",
        "tutor_reply": "💪 Напишите, какой именно репетитор вам нужен.",
        "profile_text": "🧾 Раздел «Моя анкета» в разработке.",
        "premium_text": "💎 Раздел Premium в разработке.",
        "complain_text": "⚠️ Напишите вашу жалобу одним сообщением, и администратор её увидит.",
        "complaint_sent": "✅ Жалоба отправлена администратору.",
        "send_file_now": "📎 Теперь можете отправить файл.",
        "commands": {
            "myprofile": "Моя анкета",
            "premium": "Premium",
            "complaint": "Пожаловаться",
            "language": "Язык",
        },
    },
}

for extra_lang in ["kk", "id", "ms", "es", "km", "pl", "it", "pt", "uz"]:
    TEXTS[extra_lang] = dict(TEXTS["en"])


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
    if code.startswith("kk"):
        return "kk"
    if code.startswith("id"):
        return "id"
    if code.startswith("ms"):
        return "ms"
    if code.startswith("es"):
        return "es"
    if code.startswith("km"):
        return "km"
    if code.startswith("pl"):
        return "pl"
    if code.startswith("it"):
        return "it"
    if code.startswith("pt"):
        return "pt"
    if code.startswith("uz"):
        return "uz"

    return None


async def set_bot_commands():
    commands = [
        BotCommand("myprofile", "Моя анкета"),
        BotCommand("premium", "Premium"),
        BotCommand("complaint", "Поскаржитися"),
        BotCommand("language", "Мова"),
    ]
    await bot.set_my_commands(commands)


def get_language_keyboard(include_back=False, lang="ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🇺🇦 Українська"), KeyboardButton("🇬🇧 English"))
    kb.row(KeyboardButton("🇰🇿 Қазақ"), KeyboardButton("🇮🇩 Indonesia"))
    kb.row(KeyboardButton("🇲🇾 Malay"), KeyboardButton("🇪🇸 Español"))
    kb.row(KeyboardButton("🇰🇭 ភាសាខ្មែរ"), KeyboardButton("🇵🇱 Polski"))
    kb.row(KeyboardButton("🇮🇹 Italiano"), KeyboardButton("🇵🇹🇧🇷 Portuguesa"))
    kb.row(KeyboardButton("🇺🇿 Oʻzbekcha"), KeyboardButton("🇷🇺 Русский"))

    if include_back:
        kb.row(KeyboardButton(TEXTS[lang]["back"]))

    return kb


def get_main_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(TEXTS[lang]["task"]))
    kb.row(KeyboardButton(TEXTS[lang]["tutor"]))
    kb.row(KeyboardButton(TEXTS[lang]["menu_btn"]))
    return kb


def get_task_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(TEXTS[lang]["one"]))
    kb.row(KeyboardButton(TEXTS[lang]["complex"]))
    kb.row(KeyboardButton(TEXTS[lang]["back"]))
    return kb


def get_extra_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(TEXTS[lang]["profile"]))
    kb.row(KeyboardButton(TEXTS[lang]["premium"]))
    kb.row(KeyboardButton(TEXTS[lang]["complain"]))
    kb.row(KeyboardButton(TEXTS[lang]["language"]))
    kb.row(KeyboardButton(TEXTS[lang]["back"]))
    return kb


def get_back_only_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(TEXTS[lang]["back"]))
    return kb


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    detected_lang = detect_user_language(message.from_user.language_code)

    if detected_lang:
        user_lang[message.from_user.id] = detected_lang
        user_state[message.from_user.id] = "main"
        await message.answer(
            TEXTS[detected_lang]["home"],
            reply_markup=get_main_menu(detected_lang)
        )
        return

    user_state[message.from_user.id] = "start_language"
    await message.answer(
        TEXTS["ua"]["language_text"],
        reply_markup=get_language_keyboard()
    )


@dp.message_handler(commands=["myprofile"])
async def cmd_myprofile(message: types.Message):
    lang = user_lang.get(message.from_user.id, detect_user_language(message.from_user.language_code) or "ua")
    user_lang[message.from_user.id] = lang
    user_state[message.from_user.id] = "profile_screen"
    await message.answer(TEXTS[lang]["profile_text"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["premium"])
async def cmd_premium(message: types.Message):
    lang = user_lang.get(message.from_user.id, detect_user_language(message.from_user.language_code) or "ua")
    user_lang[message.from_user.id] = lang
    user_state[message.from_user.id] = "premium_screen"
    await message.answer(TEXTS[lang]["premium_text"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["complaint"])
async def cmd_complaint(message: types.Message):
    lang = user_lang.get(message.from_user.id, detect_user_language(message.from_user.language_code) or "ua")
    user_lang[message.from_user.id] = lang
    user_state[message.from_user.id] = "complaint_wait"
    await message.answer(TEXTS[lang]["complain_text"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["language"])
async def cmd_language(message: types.Message):
    lang = user_lang.get(message.from_user.id, detect_user_language(message.from_user.language_code) or "ua")
    user_lang[message.from_user.id] = lang
    user_state[message.from_user.id] = "language_menu"
    await message.answer(
        TEXTS[lang]["language_text"],
        reply_markup=get_language_keyboard(include_back=True, lang=lang)
    )


@dp.message_handler(lambda m: m.text in LANG_BUTTONS)
async def set_language(message: types.Message):
    lang = LANG_BUTTONS[message.text]
    previous_state = user_state.get(message.from_user.id, "start_language")

    user_lang[message.from_user.id] = lang

    if previous_state == "language_menu":
        user_state[message.from_user.id] = "extra_menu"
        await message.answer(TEXTS[lang]["home"], reply_markup=get_extra_menu(lang))
    else:
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    lang = user_lang.get(message.from_user.id, "ua")
    payload = message.successful_payment.invoice_payload

    if payload == "task_payment":
        user_payment[message.from_user.id] = "task"
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_task']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=get_back_only_menu(lang)
        )

    elif payload == "complex_payment":
        user_payment[message.from_user.id] = "complex"
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_complex']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=get_back_only_menu(lang)
        )


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

    await message.answer(TEXTS[lang]["file_sent"], reply_markup=get_main_menu(lang))

    del user_payment[message.from_user.id]
    user_state[message.from_user.id] = "main"


@dp.message_handler(content_types=types.ContentType.TEXT)
async def menu(message: types.Message):
    lang = user_lang.get(message.from_user.id)
    state = user_state.get(message.from_user.id, "main")

    if not lang:
        detected_lang = detect_user_language(message.from_user.language_code)

        if detected_lang:
            user_lang[message.from_user.id] = detected_lang
            user_state[message.from_user.id] = "main"
            await message.answer(TEXTS[detected_lang]["home"], reply_markup=get_main_menu(detected_lang))
            return

        user_state[message.from_user.id] = "start_language"
        await message.answer(TEXTS["ua"]["language_text"], reply_markup=get_language_keyboard())
        return

    text = message.text

    if text == TEXTS[lang]["back"]:
        if state in ["task_menu", "extra_menu", "tutor_screen", "profile_screen", "premium_screen", "complaint_wait", "awaiting_file"]:
            user_state[message.from_user.id] = "main"
            await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))
            return

        if state == "language_menu":
            user_state[message.from_user.id] = "extra_menu"
            await message.answer(TEXTS[lang]["home"], reply_markup=get_extra_menu(lang))
            return

        await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))
        return

    if state == "complaint_wait":
        complaint_text = message.text

        caption = f"⚠️ New complaint\nUser ID: {message.from_user.id}\n"
        if message.from_user.username:
            caption += f"Username: @{message.from_user.username}\n"
        caption += f"\n{complaint_text}"

        await bot.send_message(OWNER_ID, caption)
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["complaint_sent"], reply_markup=get_main_menu(lang))
        return

    if text == TEXTS[lang]["task"]:
        user_state[message.from_user.id] = "task_menu"
        await message.answer(TEXTS[lang]["choose_service"], reply_markup=get_task_menu(lang))
        return

    if text == TEXTS[lang]["tutor"]:
        user_state[message.from_user.id] = "tutor_screen"
        await message.answer(TEXTS[lang]["tutor_reply"], reply_markup=get_back_only_menu(lang))
        return

    if text == TEXTS[lang]["menu_btn"]:
        user_state[message.from_user.id] = "extra_menu"
        await message.answer(TEXTS[lang]["home"], reply_markup=get_extra_menu(lang))
        return

    if text == TEXTS[lang]["one"]:
        user_state[message.from_user.id] = "task_menu"
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
        return

    if text == TEXTS[lang]["complex"]:
        user_state[message.from_user.id] = "task_menu"
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
        return

    if text == TEXTS[lang]["profile"]:
        user_state[message.from_user.id] = "profile_screen"
        await message.answer(TEXTS[lang]["profile_text"], reply_markup=get_back_only_menu(lang))
        return

    if text == TEXTS[lang]["premium"]:
        user_state[message.from_user.id] = "premium_screen"
        await message.answer(TEXTS[lang]["premium_text"], reply_markup=get_back_only_menu(lang))
        return

    if text == TEXTS[lang]["complain"]:
        user_state[message.from_user.id] = "complaint_wait"
        await message.answer(TEXTS[lang]["complain_text"], reply_markup=get_back_only_menu(lang))
        return

    if text == TEXTS[lang]["language"]:
        user_state[message.from_user.id] = "language_menu"
        await message.answer(
            TEXTS[lang]["language_text"],
            reply_markup=get_language_keyboard(include_back=True, lang=lang)
        )
        return

    await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))


async def on_startup(_):
    await set_bot_commands()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)