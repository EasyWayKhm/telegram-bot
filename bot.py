import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone

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
user_temp = {}
user_history = {}

REQUEST_STATUS_NEW = "new"
REQUEST_STATUS_ACCEPTED = "accepted"
REQUEST_STATUS_IN_PROGRESS = "in_progress"
REQUEST_STATUS_DONE = "done"

LANG_BUTTONS = {
    "🇺🇦 Українська": "ua",
    "🇷🇺 Русский": "ru",
}

LANG_NAMES = {
    "ua": "Українська",
    "ru": "Русский",
}

TEXTS = {
    "ua": {
        "language_text": "👋 Вибери мову бота",
        "main_menu_hint": "👋 Обери дію",
        "task": "Виконати завдання🙏",
        "tutor": "Потрібен репетитор💪",
        "my_requests_btn": "📂 Мої заявки",
        "support_btn": "🆘 Підтримка",
        "menu_btn": "📋 Меню",
        "back": "⬅️ Назад",

        "one": "Одне завдання",
        "complex": "Комплексне виконання роботи",
        "premium_profile": "Преміум профіль",
        "premium_profile_info": "Увесь місяць тобі доступна необмежена кількість завдань з будь якого шкільного предмету",
        "pay_premium_profile_btn": "Оплатити преміум профіль (2500⭐)",
        "profile_upgrade_btn": "🚀 Прокачати профіль до Premium рівня",
        "choose_service": "👇 Обери послугу",

        "file_sent": "📩 Файл відправлено адміністратору.",
        "no_payment": "❌ Спочатку потрібно оплатити.",
        "send_file_now": "📎 Тепер можеш надіслати файл.",
        "pay_success_task": "✅ Оплата 200⭐ пройшла успішно.",
        "pay_success_complex": "✅ Оплата 600⭐ пройшла успішно.",
        "pay_success_premium_profile": "✅ Оплата 2500⭐ за преміум профіль пройшла успішно.",
        "premium_profile_activated": "💎 Преміум профіль активовано на 30 днів.",

        "system_menu_title": "📋 Меню",
        "my_profile_btn": "👤 Моя анкета",
        "premium_menu_btn": "⭐ Premium профіль",
        "admin_login_btn": "🔐 Вхід адміністратора",
        "admin_profile_btn": "🛠 Admin профіль",
        "admin_logout_btn": "🚪 Вийти з адмін-профілю",
        "admin_logout_success": "✅ Ти вийшов з адмін-профілю.",

        "profile_title": "👤 Моя анкета",
        "profile_role": "Тип профілю",
        "profile_language": "Мова бота",
        "profile_status": "Статус",
        "profile_until": "Преміум активний до",
        "profile_user": "Користувач",
        "profile_admin": "Адміністратор",
        "profile_basic": "Базовий профіль",
        "profile_premium": "Преміум профіль",
        "payments_history_title": "💳 Історія оплат",
        "orders_history_title": "📦 Історія заявок",
        "no_payments_history": "Історія оплат поки порожня.",
        "no_requests": "У тебе ще немає заявок.",
        "change_language_btn": "🌍 Змінити мову",

        "complain_text": "🆘 Напиши своє питання одним повідомленням, і адміністратор отримає його.",
        "complaint_sent": "✅ Повідомлення відправлено адміністратору.",
        "complaint_header": "🆘 Нове повідомлення",
        "complaint_user_id": "ID користувача",
        "complaint_username": "Username",
        "complaint_language": "Мова",
        "complaint_profile": "Профіль",
        "complaint_text_label": "Текст",

        "support_text": "🆘 Напиши своє питання одним повідомленням, і адміністратор отримає його.",
        "support_sent": "✅ Повідомлення відправлено адміністратору.",

        "ask_admin_login": "Введи логін адміністратора:",
        "ask_admin_password": "Введи пароль адміністратора:",
        "admin_login_success": "✅ Вхід адміністратора успішний.",
        "admin_login_fail": "❌ Невірний логін або пароль.",
        "admin_panel_title": "🛠 Адмін-панель",
        "admin_new_requests_btn": "📥 Нові заявки",
        "admin_premium_users_btn": "💎 Преміум-користувачі",
        "admin_search_btn": "🔎 Пошук",
        "admin_reply_btn": "💬 Відповісти клієнту",
        "admin_no_new_requests": "Немає нових заявок.",
        "admin_no_premium_users": "Немає активних преміум-користувачів.",
        "admin_search_prompt": "Введи ID користувача:",
        "admin_reply_prompt": "Введи ID користувача, якому хочеш відповісти:",
        "admin_reply_text_prompt": "Введи текст відповіді для користувача:",
        "admin_reply_sent": "✅ Повідомлення користувачу відправлено.",

        "request_status_new": "Нова",
        "request_status_accepted": "Прийнята",
        "request_status_in_progress": "В роботі",
        "request_status_done": "Завершена",

        "premium_expire_3days": "⏳ Твій преміум закінчиться через 3 дні.",
        "premium_expired": "⚠️ Твій преміум завершився. Профіль знову став базовим.",

        "confirm_btn": "✅ Підтвердити",
        "edit_btn": "✏️ Редагувати",
        "request_confirm_text": "Перевір дані заявки перед відправкою:",
        "choose_valid_subject": "Будь ласка, обери предмет кнопкою зі списку.",
        "categories_title": "📚 Обери категорію предмета:",
        "tutor_subject_title": "Вибери предмет з якого тобі потрібен репетитор:",
        "enter_name": "Введи своє ім'я:",
        "enter_phone": "Введи свій номер телефону для зв'язку:",
        "ask_level": "Вкажи свій рівень або клас:",
        "ask_goal": "Напиши коротко свою ціль або проблему:",
        "ask_time": "Напиши зручний час для занять:",
        "ask_format": "Вкажи формат: онлайн / офлайн:",
        "tutor_request_sent": "✅ Заявку відправлено адміністратору. З тобою зв'яжуться.",
        "tutor_request_header": "📚 Нова заявка на репетитора",
        "tutor_subject": "Предмет",
        "tutor_name": "Ім'я",
        "tutor_phone": "Телефон",
        "phone_invalid": "❌ Будь ласка, введи коректний номер телефону або натисни кнопку.",
        "no_access": "⛔ Немає доступу.",
        "user_not_found": "Користувача не знайдено.",
        "error_try_again": "Помилка. Спробуй ще раз.",
        "admin_message_prefix": "💬 Повідомлення від адміністратора:\n\n",
        "new_order_prefix": "📥 New order",
        "user_id_label": "User ID",
        "username_label": "Username",
        "category_label": "Категорія",
        "level_label": "Рівень / клас",
        "goal_label": "Ціль / проблема",
        "preferred_time_label": "Зручний час",
        "format_label": "Формат",
        "status_label": "Статус",
        "user_search_title": "🔎 Користувач",
    },
    "ru": {
        "language_text": "👋 Выберите язык бота",
        "main_menu_hint": "👋 Выберите действие",
        "task": "Выполнить задание🙏",
        "tutor": "Нужен репетитор💪",
        "my_requests_btn": "📂 Мои заявки",
        "support_btn": "🆘 Поддержка",
        "menu_btn": "📋 Меню",
        "back": "⬅️ Назад",

        "one": "Одно задание",
        "complex": "Комплексное выполнение работы",
        "premium_profile": "Премиум профиль",
        "premium_profile_info": "Весь месяц тебе доступно неограниченное количество заданий по любому школьному предмету",
        "pay_premium_profile_btn": "Оплатить премиум профиль (2500⭐)",
        "profile_upgrade_btn": "🚀 Прокачать профиль до Premium уровня",
        "choose_service": "👇 Выберите услугу",

        "file_sent": "📩 Файл отправлен администратору.",
        "no_payment": "❌ Сначала нужно оплатить.",
        "send_file_now": "📎 Теперь можешь отправить файл.",
        "pay_success_task": "✅ Оплата 200⭐ прошла успешно.",
        "pay_success_complex": "✅ Оплата 600⭐ прошла успешно.",
        "pay_success_premium_profile": "✅ Оплата 2500⭐ за премиум профиль прошла успешно.",
        "premium_profile_activated": "💎 Премиум профиль активирован на 30 дней.",

        "system_menu_title": "📋 Меню",
        "my_profile_btn": "👤 Моя анкета",
        "premium_menu_btn": "⭐ Premium профиль",
        "admin_login_btn": "🔐 Вход администратора",
        "admin_profile_btn": "🛠 Admin профиль",
        "admin_logout_btn": "🚪 Выйти из админ-профиля",
        "admin_logout_success": "✅ Ты вышел из админ-профиля.",

        "profile_title": "👤 Моя анкета",
        "profile_role": "Тип профиля",
        "profile_language": "Язык бота",
        "profile_status": "Статус",
        "profile_until": "Премиум активен до",
        "profile_user": "Пользователь",
        "profile_admin": "Администратор",
        "profile_basic": "Базовый профиль",
        "profile_premium": "Премиум профиль",
        "payments_history_title": "💳 История оплат",
        "orders_history_title": "📦 История заявок",
        "no_payments_history": "История оплат пока пуста.",
        "no_requests": "У тебя ещё нет заявок.",
        "change_language_btn": "🌍 Изменить язык",

        "complain_text": "🆘 Напиши свой вопрос одним сообщением, и администратор его получит.",
        "complaint_sent": "✅ Сообщение отправлено администратору.",
        "complaint_header": "🆘 Новое сообщение",
        "complaint_user_id": "ID пользователя",
        "complaint_username": "Username",
        "complaint_language": "Язык",
        "complaint_profile": "Профиль",
        "complaint_text_label": "Текст",

        "support_text": "🆘 Напиши свой вопрос одним сообщением, и администратор его получит.",
        "support_sent": "✅ Сообщение отправлено администратору.",

        "ask_admin_login": "Введите логин администратора:",
        "ask_admin_password": "Введите пароль администратора:",
        "admin_login_success": "✅ Вход администратора успешный.",
        "admin_login_fail": "❌ Неверный логин или пароль.",
        "admin_panel_title": "🛠 Админ-панель",
        "admin_new_requests_btn": "📥 Новые заявки",
        "admin_premium_users_btn": "💎 Премиум-пользователи",
        "admin_search_btn": "🔎 Поиск",
        "admin_reply_btn": "💬 Ответить клиенту",
        "admin_no_new_requests": "Нет новых заявок.",
        "admin_no_premium_users": "Нет активных премиум-пользователей.",
        "admin_search_prompt": "Введите ID пользователя:",
        "admin_reply_prompt": "Введите ID пользователя, которому хотите ответить:",
        "admin_reply_text_prompt": "Введите текст ответа для пользователя:",
        "admin_reply_sent": "✅ Сообщение пользователю отправлено.",

        "request_status_new": "Новая",
        "request_status_accepted": "Принята",
        "request_status_in_progress": "В работе",
        "request_status_done": "Завершена",

        "premium_expire_3days": "⏳ Твой премиум закончится через 3 дня.",
        "premium_expired": "⚠️ Твой премиум завершился. Профиль снова стал базовым.",

        "confirm_btn": "✅ Подтвердить",
        "edit_btn": "✏️ Редактировать",
        "request_confirm_text": "Проверь данные заявки перед отправкой:",
        "choose_valid_subject": "Пожалуйста, выбери предмет кнопкой из списка.",
        "categories_title": "📚 Выбери категорию предмета:",
        "tutor_subject_title": "Выбери предмет, по которому тебе нужен репетитор:",
        "enter_name": "Введи своё имя:",
        "enter_phone": "Введи свой номер телефона для связи:",
        "ask_level": "Укажи свой уровень или класс:",
        "ask_goal": "Напиши кратко свою цель или проблему:",
        "ask_time": "Напиши удобное время для занятий:",
        "ask_format": "Укажи формат: онлайн / офлайн:",
        "tutor_request_sent": "✅ Заявка отправлена администратору. С тобой свяжутся.",
        "tutor_request_header": "📚 Новая заявка на репетитора",
        "tutor_subject": "Предмет",
        "tutor_name": "Имя",
        "tutor_phone": "Телефон",
        "phone_invalid": "❌ Пожалуйста, введи корректный номер телефона или нажми кнопку.",
        "no_access": "⛔ Немає доступу.",
        "user_not_found": "Пользователь не найден.",
        "error_try_again": "Ошибка. Попробуй ещё раз.",
        "admin_message_prefix": "💬 Сообщение от администратора:\n\n",
        "new_order_prefix": "📥 New order",
        "user_id_label": "User ID",
        "username_label": "Username",
        "category_label": "Категория",
        "level_label": "Уровень / класс",
        "goal_label": "Цель / проблема",
        "preferred_time_label": "Удобное время",
        "format_label": "Формат",
        "status_label": "Статус",
        "user_search_title": "🔎 Пользователь",
    },
}


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
            pending_payment TEXT,
            premium_remind_3days_sent INTEGER DEFAULT 0,
            premium_expired_sent INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tutor_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT,
            subject TEXT NOT NULL,
            client_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            level TEXT,
            goal TEXT,
            preferred_time TEXT,
            lesson_format TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            admin_reply TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payment_type TEXT NOT NULL,
            amount_stars INTEGER NOT NULL,
            created_at TEXT NOT NULL
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
            INSERT INTO users (
                user_id, language, manual_language, is_admin,
                premium_until, pending_payment,
                premium_remind_3days_sent, premium_expired_sent
            )
            VALUES (?, 'ua', 0, 0, NULL, NULL, 0, 0)
        """, (user_id,))
        conn.commit()

    conn.close()


def get_user(user_id: int):
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, language, manual_language, is_admin,
               premium_until, pending_payment,
               premium_remind_3days_sent, premium_expired_sent
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
        "premium_remind_3days_sent": bool(row[6]),
        "premium_expired_sent": bool(row[7]),
    }


def detect_language_code(language_code: str):
    if not language_code:
        return "ua"
    code = language_code.lower()
    if code.startswith("ru"):
        return "ru"
    return "ua"


def get_user_language(user_id: int):
    return get_user(user_id)["language"] or "ua"


def set_user_language(user_id: int, language: str, manual: bool = False):
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


def resolve_user_language(message: types.Message):
    user_id = message.from_user.id
    ensure_user(user_id)
    user = get_user(user_id)

    if user["manual_language"]:
        return user["language"] or "ua"

    detected = detect_language_code(message.from_user.language_code)
    set_user_language(user_id, detected, manual=False)
    return detected


def add_admin(user_id: int):
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    cur.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def remove_admin(user_id: int):
    if user_id == OWNER_ID:
        return
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    cur.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_admins():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM admins")
    rows = cur.fetchall()
    conn.close()

    ids = [row[0] for row in rows]
    if OWNER_ID not in ids:
        ids.append(OWNER_ID)
    return ids


def is_admin_user(user_id: int):
    return user_id in get_admins()


def add_payment(user_id: int, payment_type: str, amount: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO payment_history (user_id, payment_type, amount_stars, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        payment_type,
        amount,
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()


def get_user_payments(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT payment_type, amount_stars, created_at
        FROM payment_history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 10
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_user_requests(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, subject, status, created_at
        FROM tutor_requests
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 10
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


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
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET premium_until = ?,
            pending_payment = NULL,
            premium_remind_3days_sent = 0,
            premium_expired_sent = 0
        WHERE user_id = ?
    """, (premium_until.isoformat(), user_id))
    conn.commit()
    conn.close()


def clear_pending_payment(user_id: int):
    set_pending_payment(user_id, None)


def clear_premium_if_expired(user_id: int):
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
        cur.execute("UPDATE users SET premium_until = NULL WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


def is_premium(user_id: int):
    clear_premium_if_expired(user_id)
    return get_user(user_id)["premium_until"] is not None


def premium_until_text(user_id: int):
    clear_premium_if_expired(user_id)
    premium_until = get_user(user_id)["premium_until"]
    if not premium_until:
        return None
    dt = datetime.fromisoformat(premium_until)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def get_profile_status_text(user_id: int, lang: str = "ua"):
    return TEXTS[lang]["profile_premium"] if is_premium(user_id) else TEXTS[lang]["profile_basic"]


def get_request_status_text(status: str, lang: str):
    if status == REQUEST_STATUS_NEW:
        return TEXTS[lang]["request_status_new"]
    if status == REQUEST_STATUS_ACCEPTED:
        return TEXTS[lang]["request_status_accepted"]
    if status == REQUEST_STATUS_IN_PROGRESS:
        return TEXTS[lang]["request_status_in_progress"]
    if status == REQUEST_STATUS_DONE:
        return TEXTS[lang]["request_status_done"]
    return status


def save_tutor_request(
    user_id: int,
    category: str,
    subject: str,
    client_name: str,
    phone: str,
    level: str = "",
    goal: str = "",
    preferred_time: str = "",
    lesson_format: str = ""
):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tutor_requests (
            user_id, category, subject, client_name, phone,
            level, goal, preferred_time, lesson_format, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        category,
        subject,
        client_name,
        phone,
        level,
        goal,
        preferred_time,
        lesson_format,
        REQUEST_STATUS_NEW,
        datetime.now(timezone.utc).isoformat()
    ))
    request_id = cur.lastrowid
    conn.commit()
    conn.close()
    return request_id

def get_new_requests():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, subject, client_name, phone, created_at
        FROM tutor_requests
        WHERE status = ?
        ORDER BY id DESC
    """, (REQUEST_STATUS_NEW,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_premium_users():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, premium_until
        FROM users
        WHERE premium_until IS NOT NULL
        ORDER BY premium_until ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def search_user_by_id(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, language, is_admin, premium_until FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()

    cur.execute("""
        SELECT subject, status, created_at
        FROM tutor_requests
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 10
    """, (user_id,))
    requests = cur.fetchall()

    cur.execute("""
        SELECT payment_type, amount_stars, created_at
        FROM payment_history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 10
    """, (user_id,))
    payments = cur.fetchall()

    conn.close()
    return user, requests, payments


async def check_premium_reminders():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, language, premium_until, premium_remind_3days_sent, premium_expired_sent
        FROM users
        WHERE premium_until IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    now = datetime.now(timezone.utc)

    for user_id, language, premium_until, remind_3days_sent, expired_sent in rows:
        try:
            dt = datetime.fromisoformat(premium_until)
        except Exception:
            continue

        delta = dt - now

        if timedelta(days=2, hours=23) <= delta <= timedelta(days=3, hours=1):
            if not remind_3days_sent:
                try:
                    await bot.send_message(user_id, TEXTS[language]["premium_expire_3days"])
                    conn = db()
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET premium_remind_3days_sent = 1 WHERE user_id = ?", (user_id,))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logging.warning(f"Failed to send 3-day reminder to {user_id}: {e}")

        if dt <= now:
            if not expired_sent:
                try:
                    await bot.send_message(user_id, TEXTS[language]["premium_expired"])
                    conn = db()
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET premium_expired_sent = 1 WHERE user_id = ?", (user_id,))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logging.warning(f"Failed to send premium expired notice to {user_id}: {e}")


def build_profile_text(user_id: int, lang: str):
    user = get_user(user_id)
    role = TEXTS[lang]["profile_admin"] if is_admin_user(user_id) or user["is_admin"] else TEXTS[lang]["profile_user"]
    status = get_profile_status_text(user_id, lang)
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

    payments = get_user_payments(user_id)
    lines.append("")
    lines.append(TEXTS[lang]["payments_history_title"] + ":")

    if payments:
        for payment_type, amount_stars, created_at in payments:
            lines.append(f"• {payment_type} — {amount_stars}⭐ ({created_at[:16]})")
    else:
        lines.append(TEXTS[lang]["no_payments_history"])

    requests = get_user_requests(user_id)
    lines.append("")
    lines.append(TEXTS[lang]["orders_history_title"] + ":")

    if requests:
        for request_id, subject, status_code, created_at in requests:
            lines.append(f"• #{request_id} | {subject} | {get_request_status_text(status_code, lang)} | {created_at[:16]}")
    else:
        lines.append(TEXTS[lang]["no_requests"])

    return "\n".join(lines)


def main_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["task"])
    kb.row(TEXTS[lang]["tutor"])
    kb.row(TEXTS[lang]["my_requests_btn"], TEXTS[lang]["support_btn"])
    kb.row(TEXTS[lang]["menu_btn"])
    return kb


def back_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["back"])
    return kb


def system_menu(lang: str = "ua", is_admin: bool = False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["my_profile_btn"])

    if is_admin:
        kb.row(TEXTS[lang]["admin_profile_btn"])
        kb.row(TEXTS[lang]["admin_logout_btn"])
    else:
        kb.row(TEXTS[lang]["premium_menu_btn"])
        kb.row(TEXTS[lang]["admin_login_btn"])

    kb.row(TEXTS[lang]["back"])
    return kb


def premium_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["pay_premium_profile_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def profile_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["change_language_btn"])
    kb.row(TEXTS[lang]["profile_upgrade_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def admin_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["admin_new_requests_btn"])
    kb.row(TEXTS[lang]["admin_premium_users_btn"])
    kb.row(TEXTS[lang]["admin_search_btn"])
    kb.row(TEXTS[lang]["admin_reply_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


SUBJECT_CATEGORIES = {
    "📚 Предмети": [
        "Математика",
        "Англійська",
    ],
}


def get_language_keyboard(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🇺🇦 Українська", "🇷🇺 Русский")
    kb.row(TEXTS[lang]["back"])
    return kb


def get_task_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["one"])
    kb.row(TEXTS[lang]["complex"])
    kb.row(TEXTS[lang]["premium_profile"])
    kb.row(TEXTS[lang]["back"])
    return kb


def get_tutor_categories_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for category in SUBJECT_CATEGORIES.keys():
        kb.row(category)
    kb.row(TEXTS[lang]["back"])
    return kb


def get_tutor_subjects_menu(category: str, lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    subjects = SUBJECT_CATEGORIES.get(category, [])

    row = []
    for subject in subjects:
        row.append(subject)
        if len(row) == 2:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    kb.row(TEXTS[lang]["back"])
    return kb


def get_phone_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📱 Поділитися номером", request_contact=True))
    kb.row(TEXTS[lang]["back"])
    return kb


def get_request_confirm_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["confirm_btn"], TEXTS[lang]["edit_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def push_history(user_id: int, state: str):
    user_history.setdefault(user_id, [])

    if not user_history[user_id] or user_history[user_id][-1] != state:
        user_history[user_id].append(state)

    if len(user_history[user_id]) > 30:
        user_history[user_id] = user_history[user_id][-30:]


def set_state(user_id: int, new_state: str, save_current: bool = True):
    current_state = user_state.get(user_id, "main")

    if save_current and current_state != new_state:
        push_history(user_id, current_state)

    user_state[user_id] = new_state


async def render_state(message: types.Message, lang: str, state: str):
    user_id = message.from_user.id
    is_admin = is_admin_user(user_id)

    if state == "main":
        await message.answer(TEXTS[lang]["main_menu_hint"], reply_markup=main_menu(lang))
        return

    if state == "system_menu":
        await message.answer(
            TEXTS[lang]["system_menu_title"],
            reply_markup=system_menu(lang, is_admin=is_admin)
        )
        return

    if state == "profile_screen":
        await message.answer(build_profile_text(user_id, lang), reply_markup=profile_menu(lang))
        return

    if state == "premium_profile_screen":
        await message.answer(TEXTS[lang]["premium_profile_info"], reply_markup=premium_menu(lang))
        return

    if state == "language_menu":
        await message.answer(TEXTS[lang]["language_text"], reply_markup=get_language_keyboard(lang))
        return

    if state == "task_menu":
        await message.answer(TEXTS[lang]["choose_service"], reply_markup=get_task_menu(lang))
        return

    if state == "complaint_wait":
        await message.answer(TEXTS[lang]["support_text"], reply_markup=back_menu(lang))
        return

    if state == "admin_panel":
        await message.answer(TEXTS[lang]["admin_panel_title"], reply_markup=admin_menu(lang))
        return

    if state == "admin_login_wait":
        await message.answer(TEXTS[lang]["ask_admin_login"], reply_markup=back_menu(lang))
        return

    if state == "admin_password_wait":
        await message.answer(TEXTS[lang]["ask_admin_password"], reply_markup=back_menu(lang))
        return

    if state == "admin_search_wait":
        await message.answer(TEXTS[lang]["admin_search_prompt"], reply_markup=back_menu(lang))
        return

    if state == "admin_reply_user_wait":
        await message.answer(TEXTS[lang]["admin_reply_prompt"], reply_markup=back_menu(lang))
        return

    if state == "admin_reply_text_wait":
        await message.answer(TEXTS[lang]["admin_reply_text_prompt"], reply_markup=back_menu(lang))
        return

    if state == "tutor_category_wait":
        await message.answer(TEXTS[lang]["categories_title"], reply_markup=get_tutor_categories_menu(lang))
        return

    if state == "tutor_subject_wait":
        category = user_temp.get(user_id, {}).get("category", "")
        await message.answer(
            TEXTS[lang]["tutor_subject_title"],
            reply_markup=get_tutor_subjects_menu(category, lang)
        )
        return

    if state == "tutor_name_wait":
        await message.answer(TEXTS[lang]["enter_name"], reply_markup=back_menu(lang))
        return

    if state == "tutor_phone_wait":
        await message.answer(TEXTS[lang]["enter_phone"], reply_markup=get_phone_menu(lang))
        return

    if state == "tutor_level_wait":
        await message.answer(TEXTS[lang]["ask_level"], reply_markup=back_menu(lang))
        return

    if state == "tutor_goal_wait":
        await message.answer(TEXTS[lang]["ask_goal"], reply_markup=back_menu(lang))
        return

    if state == "tutor_time_wait":
        await message.answer(TEXTS[lang]["ask_time"], reply_markup=back_menu(lang))
        return

    if state == "tutor_format_wait":
        await message.answer(TEXTS[lang]["ask_format"], reply_markup=back_menu(lang))
        return

    if state == "tutor_confirm_wait":
        d = user_temp.get(user_id, {})
        confirm_text = (
            f"{TEXTS[lang]['request_confirm_text']}\n\n"
            f"{TEXTS[lang]['category_label']}: {d.get('category', '-')}\n"
            f"{TEXTS[lang]['tutor_subject']}: {d.get('subject', '-')}\n"
            f"{TEXTS[lang]['tutor_name']}: {d.get('name', '-')}\n"
            f"{TEXTS[lang]['tutor_phone']}: {d.get('phone', '-')}\n"
            f"{TEXTS[lang]['level_label']}: {d.get('level', '-')}\n"
            f"{TEXTS[lang]['goal_label']}: {d.get('goal', '-')}\n"
            f"{TEXTS[lang]['preferred_time_label']}: {d.get('preferred_time', '-')}\n"
            f"{TEXTS[lang]['format_label']}: {d.get('lesson_format', '-')}"
        )
        await message.answer(confirm_text, reply_markup=get_request_confirm_menu(lang))
        return

    if state == "awaiting_file":
        await message.answer(TEXTS[lang]["send_file_now"], reply_markup=back_menu(lang))
        return

    await message.answer(TEXTS[lang]["main_menu_hint"], reply_markup=main_menu(lang))


async def go_back(message: types.Message, lang: str):
    user_id = message.from_user.id
    history = user_history.get(user_id, [])

    if not history:
        user_state[user_id] = "main"
        await render_state(message, lang, "main")
        return

    previous_state = history.pop()
    user_state[user_id] = previous_state
    await render_state(message, lang, previous_state)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    ensure_user(message.from_user.id)
    lang = resolve_user_language(message)
    user_history[message.from_user.id] = []
    set_state(message.from_user.id, "main", save_current=False)
    await message.answer(TEXTS[lang]["main_menu_hint"], reply_markup=main_menu(lang))


@dp.message_handler(commands=["myprofile"])
async def cmd_myprofile(message: types.Message):
    lang = resolve_user_language(message)
    set_state(message.from_user.id, "profile_screen")
    await message.answer(build_profile_text(message.from_user.id, lang), reply_markup=profile_menu(lang))


@dp.message_handler(commands=["premium"])
async def cmd_premium(message: types.Message):
    lang = resolve_user_language(message)
    set_state(message.from_user.id, "premium_profile_screen")
    await message.answer(TEXTS[lang]["premium_profile_info"], reply_markup=premium_menu(lang))


@dp.message_handler(commands=["complaint"])
async def cmd_complaint(message: types.Message):
    lang = resolve_user_language(message)
    set_state(message.from_user.id, "complaint_wait")
    await message.answer(TEXTS[lang]["support_text"], reply_markup=back_menu(lang))


@dp.message_handler(commands=["language"])
async def cmd_language(message: types.Message):
    lang = resolve_user_language(message)
    set_state(message.from_user.id, "language_menu")
    await message.answer(TEXTS[lang]["language_text"], reply_markup=get_language_keyboard(lang))


@dp.message_handler(commands=["admin"])
async def cmd_admin(message: types.Message):
    lang = resolve_user_language(message)
    set_state(message.from_user.id, "admin_login_wait")
    await message.answer(TEXTS[lang]["ask_admin_login"], reply_markup=back_menu(lang))


@dp.message_handler(lambda m: m.text in LANG_BUTTONS)
async def set_language(message: types.Message):
    lang = LANG_BUTTONS[message.text]
    set_user_language(message.from_user.id, lang, manual=True)
    set_state(message.from_user.id, "main", save_current=False)
    await message.answer(TEXTS[lang]["main_menu_hint"], reply_markup=main_menu(lang))


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    lang = resolve_user_language(message)
    payload = message.successful_payment.invoice_payload

    if payload == "task_payment":
        set_pending_payment(message.from_user.id, "task")
        add_payment(message.from_user.id, "Одне завдання", 200)
        set_state(message.from_user.id, "awaiting_file")
        await message.answer(
            f"{TEXTS[lang]['pay_success_task']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=back_menu(lang)
        )

    elif payload == "complex_payment":
        set_pending_payment(message.from_user.id, "complex")
        add_payment(message.from_user.id, "Комплексне виконання роботи", 600)
        set_state(message.from_user.id, "awaiting_file")
        await message.answer(
            f"{TEXTS[lang]['pay_success_complex']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=back_menu(lang)
        )

    elif payload == "premium_profile_payment":
        activate_premium(message.from_user.id, days=30)
        add_payment(message.from_user.id, "Преміум профіль", 2500)
        set_state(message.from_user.id, "main", save_current=False)
        await message.answer(
            f"{TEXTS[lang]['pay_success_premium_profile']}\n\n{TEXTS[lang]['premium_profile_activated']}",
            reply_markup=main_menu(lang)
        )


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    lang = resolve_user_language(message)
    pending_payment = get_pending_payment(message.from_user.id)

    if pending_payment not in {"task", "complex"}:
        await message.answer(TEXTS[lang]["no_payment"], reply_markup=main_menu(lang))
        return

    caption_lines = [
        f"{TEXTS[lang]['new_order_prefix']}: {pending_payment}",
        f"{TEXTS[lang]['user_id_label']}: {message.from_user.id}",
    ]

    if message.from_user.username:
        caption_lines.append(f"{TEXTS[lang]['username_label']}: @{message.from_user.username}")

    caption = "\n".join(caption_lines)

    await bot.send_document(
        chat_id=OWNER_ID,
        document=message.document.file_id,
        caption=caption
    )

    await message.answer(TEXTS[lang]["file_sent"], reply_markup=main_menu(lang))
    clear_pending_payment(message.from_user.id)
    set_state(message.from_user.id, "main", save_current=False)