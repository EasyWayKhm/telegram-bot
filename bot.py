import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, BotCommand
from aiogram.utils import executor

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "510644962"))
ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")
DB_PATH = os.getenv("DB_PATH", "bot.db")

if not API_TOKEN:
    raise ValueError("API_TOKEN not found. Add it to .env or Railway Variables.")

db_dir = os.path.dirname(DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_state = {}

LANG_BUTTONS = {
    "🇺🇦 Українська": "ua",
    "🇷🇺 Русский": "ru",
    "🇬🇧 English": "en",
    "🇩🇪 Deutsch": "de",
    "🇫🇷 Français": "fr",
    "🇮🇹 Italiano": "it",
    "🇪🇸 Español": "es",
    "🇫🇮 Suomi": "fi",
    "🇰🇿 Қазақ": "kk",
    "🇮🇩 Indonesia": "id",
    "🇲🇾 Malay": "ms",
    "🇰🇭 ភាសាខ្មែរ": "km",
    "🇵🇱 Polski": "pl",
    "🇵🇹🇧🇷 Portuguesa": "pt",
    "🇺🇿 Oʻzbekcha": "uz",
}

LANG_NAMES = {
    "ua": "Українська",
    "ru": "Русский",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "it": "Italiano",
    "es": "Español",
    "fi": "Suomi",
    "kk": "Қазақ",
    "id": "Indonesia",
    "ms": "Malay",
    "km": "ភាសាខ្មែរ",
    "pl": "Polski",
    "pt": "Portuguesa",
    "uz": "Oʻzbekcha",
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
        "admin_login_btn": "🔐 Вхід адміністратора",
        "logout_admin_btn": "🚪 Вийти з адмін-режиму",
        "one": "Одне завдання",
        "complex": "Комплексне виконання роботи",
        "premium_profile": "Преміум профіль",
        "premium_profile_info": "Увесь місяць тобі доступна необмежена кількість завдань з будь якого шкільного предмету",
        "pay_premium_profile_btn": "Оплатити преміум профіль (2500⭐)",
        "choose_service": "👇 Обери послугу",
        "pay_success_task": "✅ Оплата 200⭐ пройшла успішно.",
        "pay_success_complex": "✅ Оплата 600⭐ пройшла успішно.",
        "pay_success_premium_profile": "✅ Оплата 2500⭐ за преміум профіль пройшла успішно.",
        "file_sent": "📩 Файл відправлено адміністратору.",
        "no_payment": "❌ Спочатку потрібно оплатити.",
        "tutor_reply": "💪 Напиши, який саме репетитор тобі потрібен.",
        "profile_title": "👤 Моя анкета",
        "profile_user": "Користувач",
        "profile_admin": "Адміністратор",
        "profile_basic": "Базовий профіль",
        "profile_premium": "Преміум профіль",
        "profile_language": "Мова бота",
        "profile_role": "Тип профілю",
        "profile_status": "Статус",
        "profile_until": "Преміум активний до",
        "premium_text": "💎 Меню Premium",
        "complain_text": "⚠️ Напиши свою скаргу одним повідомленням, і адміністратор її побачить.",
        "complaint_sent": "✅ Скаргу відправлено адміністраторам.",
        "send_file_now": "📎 Тепер можеш надіслати файл.",
        "premium_profile_activated": "💎 Преміум профіль активовано на 30 днів.",
        "ask_admin_login": "Введи логін адміністратора:",
        "ask_admin_password": "Введи пароль адміністратора:",
        "admin_login_success": "✅ Вхід адміністратора успішний.",
        "admin_login_fail": "❌ Невірний логін або пароль.",
        "admin_logged_out": "✅ Адмін-режим вимкнено.",
        "complaint_header": "⚠️ Нова скарга",
        "complaint_user_id": "ID користувача",
        "complaint_username": "Username",
        "complaint_language": "Мова",
        "complaint_profile": "Профіль",
        "complaint_text_label": "Текст скарги",
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
        "admin_login_btn": "🔐 Вход администратора",
        "logout_admin_btn": "🚪 Выйти из админ-режима",
        "one": "Одно задание",
        "complex": "Комплексное выполнение работы",
        "premium_profile": "Премиум профиль",
        "premium_profile_info": "Целый месяц тебе доступно неограниченное количество заданий по любому школьному предмету",
        "pay_premium_profile_btn": "Оплатить премиум профиль (2500⭐)",
        "choose_service": "👇 Выберите услугу",
        "pay_success_task": "✅ Оплата 200⭐ прошла успешно.",
        "pay_success_complex": "✅ Оплата 600⭐ прошла успешно.",
        "pay_success_premium_profile": "✅ Оплата 2500⭐ за премиум профиль прошла успешно.",
        "file_sent": "📩 Файл отправлен администратору.",
        "no_payment": "❌ Сначала нужно оплатить.",
        "tutor_reply": "💪 Напишите, какой именно репетитор вам нужен.",
        "profile_title": "👤 Моя анкета",
        "profile_user": "Пользователь",
        "profile_admin": "Администратор",
        "profile_basic": "Базовый профиль",
        "profile_premium": "Премиум профиль",
        "profile_language": "Язык бота",
        "profile_role": "Тип профиля",
        "profile_status": "Статус",
        "profile_until": "Премиум активен до",
        "premium_text": "💎 Меню Premium",
        "complain_text": "⚠️ Напишите вашу жалобу одним сообщением, и администратор её увидит.",
        "complaint_sent": "✅ Жалоба отправлена администраторам.",
        "send_file_now": "📎 Теперь можете отправить файл.",
        "premium_profile_activated": "💎 Премиум профиль активирован на 30 дней.",
        "ask_admin_login": "Введите логин администратора:",
        "ask_admin_password": "Введите пароль администратора:",
        "admin_login_success": "✅ Вход администратора успешный.",
        "admin_login_fail": "❌ Неверный логин или пароль.",
        "admin_logged_out": "✅ Админ-режим выключен.",
        "complaint_header": "⚠️ Новая жалоба",
        "complaint_user_id": "ID пользователя",
        "complaint_username": "Username",
        "complaint_language": "Язык",
        "complaint_profile": "Профиль",
        "complaint_text_label": "Текст жалобы",
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
        "admin_login_btn": "🔐 Admin login",
        "logout_admin_btn": "🚪 Log out admin mode",
        "one": "Single task",
        "complex": "Complex work",
        "premium_profile": "Premium profile",
        "premium_profile_info": "For the whole month, you get unlimited tasks in any school subject",
        "pay_premium_profile_btn": "Pay for premium profile (2500⭐)",
        "choose_service": "👇 Choose a service",
        "pay_success_task": "✅ Payment of 200⭐ was successful.",
        "pay_success_complex": "✅ Payment of 600⭐ was successful.",
        "pay_success_premium_profile": "✅ Payment of 2500⭐ for premium profile was successful.",
        "file_sent": "📩 File sent to the administrator.",
        "no_payment": "❌ You need to pay first.",
        "tutor_reply": "💪 Write what kind of tutor you need.",
        "profile_title": "👤 My profile",
        "profile_user": "User",
        "profile_admin": "Administrator",
        "profile_basic": "Basic profile",
        "profile_premium": "Premium profile",
        "profile_language": "Bot language",
        "profile_role": "Profile type",
        "profile_status": "Status",
        "profile_until": "Premium active until",
        "premium_text": "💎 Premium menu",
        "complain_text": "⚠️ Send your complaint in one message, and the administrators will receive it.",
        "complaint_sent": "✅ Complaint sent to administrators.",
        "send_file_now": "📎 Now you can send your file.",
        "premium_profile_activated": "💎 Premium profile activated for 30 days.",
        "ask_admin_login": "Enter admin login:",
        "ask_admin_password": "Enter admin password:",
        "admin_login_success": "✅ Admin login successful.",
        "admin_login_fail": "❌ Wrong login or password.",
        "admin_logged_out": "✅ Admin mode disabled.",
        "complaint_header": "⚠️ New complaint",
        "complaint_user_id": "User ID",
        "complaint_username": "Username",
        "complaint_language": "Language",
        "complaint_profile": "Profile",
        "complaint_text_label": "Complaint text",
    },
    "de": {},
    "fr": {},
    "it": {},
    "es": {},
    "fi": {},
}

for code in ["de", "fr", "it", "es", "fi", "kk", "id", "ms", "km", "pl", "pt", "uz"]:
    if code not in TEXTS or not TEXTS[code]:
        TEXTS[code] = dict(TEXTS["en"])


def db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'ua',
            manual_language INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            premium_until TEXT,
            pending_payment TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()


def ensure_user(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if not row:
        cur.execute("""
            INSERT INTO users (user_id, language, manual_language, is_admin, premium_until, pending_payment)
            VALUES (?, 'ua', 0, 0, NULL, NULL)
        """, (user_id,))
        conn.commit()

    conn.close()


def get_user(user_id: int):
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, language, manual_language, is_admin, premium_until, pending_payment
        FROM users
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()

    return {
        "user_id": row[0],
        "language": row[1],
        "manual_language": bool(row[2]),
        "is_admin": bool(row[3]),
        "premium_until": row[4],
        "pending_payment": row[5],
    }


def update_user_language(user_id: int, language: str, manual: bool):
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET language = ?, manual_language = ?
        WHERE user_id = ?
    """, (language, 1 if manual else 0, user_id))
    conn.commit()
    conn.close()


def add_admin(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def remove_admin(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_all_admin_ids():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM admins")
    rows = cur.fetchall()
    conn.close()

    admin_ids = [row[0] for row in rows]

    if OWNER_ID not in admin_ids:
        admin_ids.append(OWNER_ID)

    return admin_ids


def set_admin(user_id: int, is_admin: bool):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (1 if is_admin else 0, user_id))
    conn.commit()
    conn.close()

    if is_admin:
        add_admin(user_id)
    else:
        if user_id != OWNER_ID:
            remove_admin(user_id)


def set_pending_payment(user_id: int, payment_type: str | None):
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET pending_payment = ? WHERE user_id = ?", (payment_type, user_id))
    conn.commit()
    conn.close()


def get_pending_payment(user_id: int):
    return get_user(user_id)["pending_payment"]


def activate_premium(user_id: int, days: int = 30):
    ensure_user(user_id)
    premium_until = datetime.now(timezone.utc) + timedelta(days=days)
    premium_until_str = premium_until.isoformat()

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET premium_until = ?, pending_payment = NULL
        WHERE user_id = ?
    """, (premium_until_str, user_id))
    conn.commit()
    conn.close()


def clear_pending_payment(user_id: int):
    set_pending_payment(user_id, None)


def clear_premium_if_expired(user_id: int):
    ensure_user(user_id)
    user = get_user(user_id)
    premium_until = user["premium_until"]

    if not premium_until:
        return

    try:
        dt = datetime.fromisoformat(premium_until)
    except ValueError:
        dt = None

    if not dt or dt <= datetime.now(timezone.utc):
        conn = db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET premium_until = NULL
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()
        conn.close()


def is_premium(user_id: int):
    clear_premium_if_expired(user_id)
    user = get_user(user_id)
    return user["premium_until"] is not None


def premium_until_text(user_id: int):
    clear_premium_if_expired(user_id)
    user = get_user(user_id)
    premium_until = user["premium_until"]

    if not premium_until:
        return None

    dt = datetime.fromisoformat(premium_until)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def get_profile_status_text(user_id: int, lang: str = "ua"):
    if is_premium(user_id):
        return TEXTS[lang]["profile_premium"]
    return TEXTS[lang]["profile_basic"]


def detect_user_language(language_code: str):
    if not language_code:
        return None

    code = language_code.lower()

    if code.startswith("uk"):
        return "ua"
    if code.startswith("ru"):
        return "ru"
    if code.startswith("en"):
        return "en"
    if code.startswith("de"):
        return "de"
    if code.startswith("fr"):
        return "fr"
    if code.startswith("it"):
        return "it"
    if code.startswith("es"):
        return "es"
    if code.startswith("fi"):
        return "fi"
    if code.startswith("kk"):
        return "kk"
    if code.startswith("id"):
        return "id"
    if code.startswith("ms"):
        return "ms"
    if code.startswith("km"):
        return "km"
    if code.startswith("pl"):
        return "pl"
    if code.startswith("pt"):
        return "pt"
    if code.startswith("uz"):
        return "uz"

    return None


def resolve_user_language(message: types.Message):
    user_id = message.from_user.id
    ensure_user(user_id)
    user = get_user(user_id)

    if user["manual_language"]:
        return user["language"] or "ua"

    detected_lang = detect_user_language(message.from_user.language_code)
    if detected_lang:
        update_user_language(user_id, detected_lang, manual=False)
        return detected_lang

    return user["language"] or "ua"


def build_profile_text(user_id: int, lang: str):
    clear_premium_if_expired(user_id)
    user = get_user(user_id)

    role = TEXTS[lang]["profile_admin"] if user["is_admin"] or user_id == OWNER_ID else TEXTS[lang]["profile_user"]
    status = TEXTS[lang]["profile_premium"] if is_premium(user_id) else TEXTS[lang]["profile_basic"]
    language_name = LANG_NAMES.get(user["language"], user["language"])

    lines = [
        TEXTS[lang]["profile_title"],
        "",
        f"{TEXTS[lang]['profile_role']}: {role}",
        f"{TEXTS[lang]['profile_language']}: {language_name}",
        f"{TEXTS[lang]['profile_status']}: {status}",
    ]

    premium_until = premium_until_text(user_id)
    if premium_until:
        lines.append(f"{TEXTS[lang]['profile_until']}: {premium_until}")

    return "\n".join(lines)


async def set_bot_commands():
    commands = [
        BotCommand("myprofile", "My profile"),
        BotCommand("premium", "Premium"),
        BotCommand("complaint", "Complaint"),
        BotCommand("language", "Language"),
        BotCommand("admin", "Admin login"),
    ]
    await bot.set_my_commands(commands)


def get_language_keyboard(include_back=False, lang="ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🇺🇦 Українська", "🇷🇺 Русский")
    kb.row("🇬🇧 English", "🇩🇪 Deutsch")
    kb.row("🇫🇷 Français", "🇮🇹 Italiano")
    kb.row("🇪🇸 Español", "🇫🇮 Suomi")
    kb.row("🇰🇿 Қазақ", "🇮🇩 Indonesia")
    kb.row("🇲🇾 Malay", "🇰🇭 ភាសាខ្មែរ")
    kb.row("🇵🇱 Polski", "🇵🇹🇧🇷 Portuguesa")
    kb.row("🇺🇿 Oʻzbekcha")

    if include_back:
        kb.row(TEXTS[lang]["back"])

    return kb


def get_main_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["task"])
    kb.row(TEXTS[lang]["tutor"])
    kb.row(TEXTS[lang]["menu_btn"])
    return kb


def get_task_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["one"])
    kb.row(TEXTS[lang]["complex"])
    kb.row(TEXTS[lang]["premium_profile"])
    kb.row(TEXTS[lang]["back"])
    return kb


def get_extra_menu(lang: str, user_id: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["profile"])
    kb.row(TEXTS[lang]["premium"])
    kb.row(TEXTS[lang]["complain"])
    kb.row(TEXTS[lang]["language"])

    if get_user(user_id)["is_admin"] or user_id == OWNER_ID:
        kb.row(TEXTS[lang]["logout_admin_btn"])
    else:
        kb.row(TEXTS[lang]["admin_login_btn"])

    kb.row(TEXTS[lang]["back"])
    return kb


def get_back_only_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["back"])
    return kb


def get_premium_profile_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["pay_premium_profile_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    ensure_user(message.from_user.id)
    detected_lang = detect_user_language(message.from_user.language_code)

    if detected_lang:
        update_user_language(message.from_user.id, detected_lang, manual=False)
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[detected_lang]["home"], reply_markup=get_main_menu(detected_lang))
        return

    user_state[message.from_user.id] = "start_language"
    await message.answer(TEXTS["ua"]["language_text"], reply_markup=get_language_keyboard())


@dp.message_handler(commands=["myprofile"])
async def cmd_myprofile(message: types.Message):
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "profile_screen"
    await message.answer(build_profile_text(message.from_user.id, lang), reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["premium"])
async def cmd_premium(message: types.Message):
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "premium_profile_screen"
    await message.answer(
        TEXTS[lang]["premium_profile_info"],
        reply_markup=get_premium_profile_menu(lang)
    )


@dp.message_handler(commands=["complaint"])
async def cmd_complaint(message: types.Message):
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "complaint_wait"
    await message.answer(TEXTS[lang]["complain_text"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["language"])
async def cmd_language(message: types.Message):
    lang = resolve_user_language(message)
    update_user_language(message.from_user.id, lang, manual=False)
    user_state[message.from_user.id] = "language_menu"
    await message.answer(
        TEXTS[lang]["language_text"],
        reply_markup=get_language_keyboard(include_back=True, lang=lang)
    )


@dp.message_handler(commands=["admin"])
async def cmd_admin(message: types.Message):
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "admin_login_wait"
    await message.answer(TEXTS[lang]["ask_admin_login"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(lambda m: m.text in LANG_BUTTONS)
async def set_language(message: types.Message):
    lang = LANG_BUTTONS[message.text]
    previous_state = user_state.get(message.from_user.id, "start_language")

    update_user_language(message.from_user.id, lang, manual=True)

    if previous_state == "language_menu":
        user_state[message.from_user.id] = "extra_menu"
        await message.answer(TEXTS[lang]["home"], reply_markup=get_extra_menu(lang, message.from_user.id))
    else:
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    lang = resolve_user_language(message)
    payload = message.successful_payment.invoice_payload

    if payload == "task_payment":
        set_pending_payment(message.from_user.id, "task")
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_task']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=get_back_only_menu(lang)
        )

    elif payload == "complex_payment":
        set_pending_payment(message.from_user.id, "complex")
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_complex']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=get_back_only_menu(lang)
        )

    elif payload == "premium_profile_payment":
        activate_premium(message.from_user.id, days=30)
        user_state[message.from_user.id] = "main"
        await message.answer(
            f"{TEXTS[lang]['pay_success_premium_profile']}\n\n{TEXTS[lang]['premium_profile_activated']}",
            reply_markup=get_main_menu(lang)
        )


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    lang = resolve_user_language(message)
    pending_payment = get_pending_payment(message.from_user.id)

    if pending_payment not in {"task", "complex"}:
        await message.answer(TEXTS[lang]["no_payment"])
        return

    caption_lines = [
        f"📥 New order: {pending_payment}",
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

    clear_pending_payment(message.from_user.id)
    user_state[message.from_user.id] = "main"


@dp.message_handler(content_types=types.ContentType.TEXT)
async def menu(message: types.Message):
    lang = resolve_user_language(message)
    state = user_state.get(message.from_user.id, "main")
    text = message.text

    if text == TEXTS[lang]["back"]:
        if state in [
            "task_menu", "extra_menu", "tutor_screen", "profile_screen",
            "premium_screen", "complaint_wait", "awaiting_file",
            "premium_profile_screen", "admin_login_wait", "admin_password_wait"
        ]:
            user_state[message.from_user.id] = "main"
            await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))
            return

        if state == "language_menu":
            user_state[message.from_user.id] = "extra_menu"
            await message.answer(TEXTS[lang]["home"], reply_markup=get_extra_menu(lang, message.from_user.id))
            return

        await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))
        return

    if state == "admin_login_wait":
        user_state[message.from_user.id] = "admin_password_wait"
        user_state[f"admin_login_{message.from_user.id}"] = text
        await message.answer(TEXTS[lang]["ask_admin_password"], reply_markup=get_back_only_menu(lang))
        return

    if state == "admin_password_wait":
        login_value = user_state.get(f"admin_login_{message.from_user.id}")
        password_value = text

        if login_value == ADMIN_LOGIN and password_value == ADMIN_PASSWORD:
            set_admin(message.from_user.id, True)
            user_state[message.from_user.id] = "main"
            await message.answer(TEXTS[lang]["admin_login_success"], reply_markup=get_main_menu(lang))
        else:
            set_admin(message.from_user.id, False)
            user_state[message.from_user.id] = "main"
            await message.answer(TEXTS[lang]["admin_login_fail"], reply_markup=get_main_menu(lang))

        user_state.pop(f"admin_login_{message.from_user.id}", None)
        return

    if state == "complaint_wait":
        complaint_text = message.text
        user_id = message.from_user.id
        user = get_user(user_id)

        profile_status = get_profile_status_text(user_id, lang)
        language_name = LANG_NAMES.get(user["language"], user["language"])

        caption_lines = [
            TEXTS[lang]["complaint_header"],
            f"{TEXTS[lang]['complaint_user_id']}: {user_id}",
            f"{TEXTS[lang]['complaint_language']}: {language_name}",
            f"{TEXTS[lang]['complaint_profile']}: {profile_status}",
        ]

        if message.from_user.username:
            caption_lines.append(f"{TEXTS[lang]['complaint_username']}: @{message.from_user.username}")

        premium_until = premium_until_text(user_id)
        if premium_until:
            caption_lines.append(f"{TEXTS[lang]['profile_until']}: {premium_until}")

        caption_lines.append("")
        caption_lines.append(f"{TEXTS[lang]['complaint_text_label']}:")
        caption_lines.append(complaint_text)

        caption = "\n".join(caption_lines)

        for admin_id in get_all_admin_ids():
            try:
                await bot.send_message(admin_id, caption)
            except Exception as e:
                logging.warning(f"Failed to send complaint to admin {admin_id}: {e}")

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
        await message.answer(TEXTS[lang]["home"], reply_markup=get_extra_menu(lang, message.from_user.id))
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

    if text == TEXTS[lang]["premium_profile"]:
        user_state[message.from_user.id] = "premium_profile_screen"
        await message.answer(
            TEXTS[lang]["premium_profile_info"],
            reply_markup=get_premium_profile_menu(lang)
        )
        return

    if text == TEXTS[lang]["pay_premium_profile_btn"]:
        user_state[message.from_user.id] = "premium_profile_screen"
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Premium Profile Payment",
            description="Unlimited tasks for one month",
            payload="premium_profile_payment",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Premium Profile", amount=2500)],
            start_parameter="premium_profile"
        )
        return

    if text == TEXTS[lang]["profile"]:
        user_state[message.from_user.id] = "profile_screen"
        await message.answer(build_profile_text(message.from_user.id, lang), reply_markup=get_back_only_menu(lang))
        return

    if text == TEXTS[lang]["premium"]:
        user_state[message.from_user.id] = "premium_profile_screen"
        await message.answer(
            TEXTS[lang]["premium_profile_info"],
            reply_markup=get_premium_profile_menu(lang)
        )
        return

    if text == TEXTS[lang]["complain"]:
        user_state[message.from_user.id] = "complaint_wait"
        await message.answer(TEXTS[lang]["complain_text"], reply_markup=get_back_only_menu(lang))
        return

    if text == TEXTS[lang]["language"]:
        current_lang = resolve_user_language(message)
        update_user_language(message.from_user.id, current_lang, manual=False)
        user_state[message.from_user.id] = "language_menu"
        await message.answer(
            TEXTS[current_lang]["language_text"],
            reply_markup=get_language_keyboard(include_back=True, lang=current_lang)
        )
        return

    if text == TEXTS[lang]["admin_login_btn"]:
        user_state[message.from_user.id] = "admin_login_wait"
        await message.answer(TEXTS[lang]["ask_admin_login"], reply_markup=get_back_only_menu(lang))
        return

    if text == TEXTS[lang]["logout_admin_btn"]:
        set_admin(message.from_user.id, False)
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["admin_logged_out"], reply_markup=get_main_menu(lang))
        return

    await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))


async def on_startup(_):
    init_db()
    ensure_user(OWNER_ID)
    set_admin(OWNER_ID, True)
    add_admin(OWNER_ID)
    await set_bot_commands()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)