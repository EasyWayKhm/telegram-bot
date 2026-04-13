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
DB_PATH = os.getenv("DB_PATH", "bot.db")

if not API_TOKEN:
    raise ValueError("API_TOKEN not found")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_state = {}
user_temp = {}

# ---------------- БАЗА ----------------

def db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        premium_until TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tutor_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        subject TEXT,
        name TEXT,
        phone TEXT,
        level TEXT,
        goal TEXT,
        time TEXT,
        format TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        amount INTEGER,
        created TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_admin(user_id):
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO admins VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def get_admins():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM admins")
    rows = cur.fetchall()
    conn.close()

    ids = [r[0] for r in rows]
    if OWNER_ID not in ids:
        ids.append(OWNER_ID)
    return ids


def add_payment(user_id, type_, amount):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (user_id, type, amount, created) VALUES (?,?,?,?)",
        (user_id, type_, amount, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


# ---------------- ПРЕМІУМ ----------------

def activate_premium(user_id):
    until = datetime.now() + timedelta(days=30)

    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO users (user_id, premium_until) VALUES (?,?)",
        (user_id, until.isoformat())
    )
    conn.commit()
    conn.close()


def is_premium(user_id):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row or not row[0]:
        return False

    return datetime.fromisoformat(row[0]) > datetime.now()


# ---------------- КНОПКИ ----------------

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Виконати завдання🙏")
    kb.row("Потрібен репетитор💪")
    kb.row("📂 Мої заявки", "🆘 Підтримка")
    kb.row("🏠 Головне меню")
    return kb


def back():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("⬅️ Назад")
    return kb

# ---------------- ПРЕДМЕТИ ПО КАТЕГОРІЯХ ----------------

SUBJECT_CATEGORIES = {
    "🌍 Мови": [
        "Англійська", "Іспанська", "Французька", "Німецька", "Японська", "Італійська",
        "Корейська", "Арабська", "Китайська (Путунхуа)", "Португальська", "Російська",
        "Польська", "Турецька", "Українська", "Голландська", "Вірменська", "Норвезька",
        "Шведська", "Фінська", "Угорська", "Грузинська", "Іврит", "Хінді", "Чеська",
        "Грецька", "Телугу", "Кхмерська", "Білоруська", "Жестова", "Латинь", "Санскрит",
        "Урду", "Сербська", "Датська", "Тибетська", "Литовська", "Словацька",
        "В'єтнамська", "Тамільська", "Тагальська", "Румунська", "Ірландська",
        "Ісландська", "Перська (фарсі)", "Хорватська", "Каталанська", "Болгарська",
        "Бенгалі", "Панджабі", "Тайська", "Малаяламська", "Албанська", "Пушту",
        "Гавайська", "Есперанто", "Монгольська", "Сомалійська", "Словенська",
        "Казахська", "Тамазігхтська", "Кантонська мова", "Курдська", "Кіньяруанда",
        "Узбецька", "Маорі", "Ігбо", "Сингальська", "Бірманська", "Лаоська",
        "Йоруба", "Амхарська", "Суахілі", "Африкаанс", "Коса", "Македонська",
        "Люксембурзька", "Кечуа", "Азербайджанська", "Валлійська", "Каннада",
        "Гуджараті", "Мальтійська", "Креольська", "Ідиш", "Боснійська", "Естонська",
        "Луганда", "Кебуанська", "Баскська", "Кічуа", "Кримськотатарська",
        "Індонезійська", "Малайська"
    ],
    "🔬 Точні науки": [
        "Хімія", "Математика", "Статистика", "Економіка", "Біологія",
        "Алгебра", "Фізика", "Географія"
    ],
    "💻 IT і програмування": [
        "Інформатика", "Go language", "Rust", "Scala", "HTML", "XML", "CSS",
        "JavaScript", "NodeJS", "Python", "PHP", "Ruby", "Bash", "Java", "C",
        "Swift", "Objective C", "C++", "C#", "R", "Data Science",
        "Штучний інтелект", "Веб розробка", "Веб аналітика",
        "Розробка додатків iOS", "Розробка додатків Android", "Бази даних",
        "Алгоритми", "SEO", "UX/UI", "Управління IT проектами"
    ],
    "💼 Бізнес, маркетинг і фінанси": [
        "Бухгалтерський облік", "Корпоративне фінансування", "Бізнес аналітика",
        "Бізнес стратегія", "Управління продуктом", "PR", "Міжнародний бізнес",
        "Маркетингові стратегії", "Контент маркетинг", "Бізнес і управління",
        "SMM", "Копірайтинг", "Email маркетинг", "PPC", "Бізнес моделювання",
        "Продажі", "Юридична справа"
    ],
    "📚 Гуманітарні науки": [
        "Історія", "Література", "Філософія", "Письмо", "Тести", "Конкурсний іспит"
    ],
    "🎨 Мистецтво і креатив": [
        "Мистецтво", "Музика", "Акторська майстерність", "Живопис", "Фотографія",
        "Motion design", "Video post-production", "3D дизайн", "Графічний дизайн",
        "Ораторське мистецтво"
    ],
    "👥 Суспільні науки": [
        "Соціологія", "Суспільствознавство", "Психологія"
    ],
    "🎮 Інше": [
        "Dota 2"
    ]
}


def categories_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for category in SUBJECT_CATEGORIES.keys():
        kb.row(category)
    kb.row("⬅️ Назад")
    return kb


def subjects_menu(category):
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

    kb.row("⬅️ Назад")
    return kb


def confirm_request_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("✅ Підтвердити")
    kb.row("✏️ Редагувати")
    kb.row("⬅️ Назад")
    return kb


def phone_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton("📱 Поділитися номером", request_contact=True)
    kb.row(btn)
    kb.row("⬅️ Назад")
    return kb


def admin_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📥 Нові заявки")
    kb.row("💎 Преміум-користувачі")
    kb.row("🔎 Пошук")
    kb.row("💬 Відповісти клієнту")
    kb.row("⬅️ Назад")
    return kb

# ---------------- СТАРТ ТА КОМАНДИ ----------------

@dp.message_handler(commands=["start"])
async def start(m: types.Message):
    await m.answer("👋 Обери дію", reply_markup=main_menu())


@dp.message_handler(commands=["myprofile"])
async def myprofile_cmd(m: types.Message):
    user_id = m.from_user.id

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    profile_type = "Базовий профіль"
    premium_text = "Немає активного преміуму"

    if row and row[0]:
        try:
            until = datetime.fromisoformat(row[0])
            if until > datetime.now():
                profile_type = "Преміум профіль"
                premium_text = f"Діє до: {until.strftime('%Y-%m-%d %H:%M')}"
        except:
            pass

    is_admin = user_id in get_admins()
    role = "Адміністратор" if is_admin else "Користувач"

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT type, amount, created FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
    payments = cur.fetchall()

    cur.execute("SELECT subject, status FROM tutor_requests WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
    requests = cur.fetchall()
    conn.close()

    pay_lines = []
    if payments:
        for p in payments:
            pay_lines.append(f"• {p[0]} — {p[1]}⭐ ({p[2][:16]})")
    else:
        pay_lines.append("Історія оплат порожня")

    req_lines = []
    if requests:
        for r in requests:
            req_lines.append(f"• {r[0]} — {r[1]}")
    else:
        req_lines.append("Заявок ще немає")

    text = (
        f"👤 Моя анкета\n\n"
        f"Тип профілю: {role}\n"
        f"Статус: {profile_type}\n"
        f"{premium_text}\n\n"
        f"💳 Історія оплат і замовлень:\n" + "\n".join(pay_lines) + "\n\n"
        f"📂 Мої заявки:\n" + "\n".join(req_lines)
    )

    await m.answer(text, reply_markup=back())


@dp.message_handler(commands=["premium"])
async def premium_cmd(m: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Оплатити преміум профіль (2500⭐)")
    kb.row("⬅️ Назад")

    await m.answer(
        "Увесь місяць тобі доступна необмежена кількість завдань з будь якого шкільного предмету",
        reply_markup=kb
    )


@dp.message_handler(commands=["complaint"])
async def complaint_cmd(m: types.Message):
    user_state[m.from_user.id] = "complaint"
    await m.answer("Напиши своє повідомлення адміністратору:", reply_markup=back())


@dp.message_handler(lambda m: m.text == "🆘 Підтримка")
async def support_btn(m: types.Message):
    user_state[m.from_user.id] = "support"
    await m.answer("🆘 Напиши своє питання одним повідомленням, і адміністратор отримає його.", reply_markup=back())


@dp.message_handler(lambda m: m.text == "📂 Мої заявки")
async def my_requests(m: types.Message):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT id, subject, status FROM tutor_requests WHERE user_id=? ORDER BY id DESC", (m.from_user.id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await m.answer("У тебе ще немає заявок.", reply_markup=back())
        return

    lines = ["📂 Мої заявки:\n"]
    for r in rows:
        lines.append(f"#{r[0]} | {r[1]} | {r[2]}")

    await m.answer("\n".join(lines), reply_markup=back())


@dp.message_handler(lambda m: m.text == "🏠 Головне меню")
async def home_btn(m: types.Message):
    user_state[m.from_user.id] = "main"
    await m.answer("👋 Обери дію", reply_markup=main_menu())


# ---------------- ОПЛАТИ ----------------

@dp.pre_checkout_query_handler(lambda q: True)
async def pc(q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def paid(m: types.Message):
    payload = m.successful_payment.invoice_payload

    if payload == "task":
        add_payment(m.from_user.id, "Одне завдання", 200)
        user_state[m.from_user.id] = "send_file"
        await m.answer("✅ Оплата 200⭐ пройшла. Надішли файл.", reply_markup=back())

    elif payload == "complex":
        add_payment(m.from_user.id, "Комплексне виконання роботи", 600)
        user_state[m.from_user.id] = "send_file"
        await m.answer("✅ Оплата 600⭐ пройшла. Надішли файл.", reply_markup=back())

    elif payload == "premium":
        add_payment(m.from_user.id, "Преміум профіль", 2500)
        activate_premium(m.from_user.id)
        await m.answer("💎 Преміум профіль активовано на 30 днів.", reply_markup=main_menu())


@dp.message_handler(lambda m: m.text == "Одне завдання")
async def one_task(m: types.Message):
    await bot.send_invoice(
        chat_id=m.chat.id,
        title="Одне завдання",
        description="Оплата одного завдання",
        payload="task",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Одне завдання", 200)],
        start_parameter="task"
    )


@dp.message_handler(lambda m: m.text == "Комплексне виконання роботи")
async def complex_task(m: types.Message):
    await bot.send_invoice(
        chat_id=m.chat.id,
        title="Комплексне виконання роботи",
        description="Оплата комплексного виконання роботи",
        payload="complex",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Комплексне виконання роботи", 600)],
        start_parameter="complex"
    )


@dp.message_handler(lambda m: m.text == "Оплатити преміум профіль (2500⭐)")
async def premium_payment(m: types.Message):
    await bot.send_invoice(
        chat_id=m.chat.id,
        title="Преміум профіль",
        description="Необмежена кількість завдань протягом 30 днів",
        payload="premium",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Преміум профіль", 2500)],
        start_parameter="premium"
    )


# ---------------- ФАЙЛ ПІСЛЯ ОПЛАТИ ----------------

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def doc_handler(m: types.Message):
    if user_state.get(m.from_user.id) != "send_file":
        await m.answer("❌ Спочатку потрібно оплатити.", reply_markup=main_menu())
        return

    await bot.send_document(
        OWNER_ID,
        m.document.file_id,
        caption=f"📥 Новий файл від користувача {m.from_user.id}"
    )

    await m.answer("📩 Файл відправлено адміністратору.", reply_markup=main_menu())
    user_state[m.from_user.id] = "main"


# ---------------- НАГАДУВАННЯ ПРО ПРЕМІУМ ----------------

async def check_premium_reminders():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, premium_until FROM users WHERE premium_until IS NOT NULL")
    users = cur.fetchall()
    conn.close()

    now = datetime.now()

    for user_id, premium_until in users:
        try:
            end_date = datetime.fromisoformat(premium_until)
        except:
            continue

        delta = end_date - now

        if timedelta(days=2, hours=23) <= delta <= timedelta(days=3, hours=1):
            try:
                await bot.send_message(user_id, "⏳ Твій преміум закінчиться через 3 дні.")
            except:
                pass

        if timedelta(hours=-1) <= delta <= timedelta(hours=1):
            try:
                await bot.send_message(user_id, "⚠️ Твій преміум завершився. Профіль знову став базовим.")
            except:
                pass

# ---------------- РЕПЕТИТОР: КАТЕГОРІЯ -> ПРЕДМЕТ -> АНКЕТА ----------------

@dp.message_handler(lambda m: m.text == "Потрібен репетитор💪")
async def tutor_start(m: types.Message):
    user_state[m.from_user.id] = "tutor_category"
    user_temp[m.from_user.id] = {}
    await m.answer(
        "Вибери категорію предмета:",
        reply_markup=categories_menu()
    )


@dp.message_handler(lambda m: m.text in SUBJECT_CATEGORIES.keys())
async def tutor_choose_category(m: types.Message):
    if user_state.get(m.from_user.id) != "tutor_category":
        return

    user_temp[m.from_user.id]["category"] = m.text
    user_state[m.from_user.id] = "tutor_subject"

    await m.answer(
        "Вибери предмет з якого тобі потрібен репетитор зі списку:",
        reply_markup=subjects_menu(m.text)
    )


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_subject")
async def tutor_choose_subject(m: types.Message):
    category = user_temp.get(m.from_user.id, {}).get("category")
    valid_subjects = SUBJECT_CATEGORIES.get(category, [])

    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "tutor_category"
        await m.answer("Вибери категорію предмета:", reply_markup=categories_menu())
        return

    if m.text not in valid_subjects:
        await m.answer("Будь ласка, обери предмет кнопкою зі списку.", reply_markup=subjects_menu(category))
        return

    user_temp[m.from_user.id]["subject"] = m.text
    user_state[m.from_user.id] = "tutor_name"

    await m.answer("Введи своє ім'я:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_name")
async def tutor_name(m: types.Message):
    if m.text == "⬅️ Назад":
        category = user_temp.get(m.from_user.id, {}).get("category")
        user_state[m.from_user.id] = "tutor_subject"
        await m.answer(
            "Вибери предмет з якого тобі потрібен репетитор зі списку:",
            reply_markup=subjects_menu(category)
        )
        return

    user_temp[m.from_user.id]["name"] = m.text.strip()
    user_state[m.from_user.id] = "tutor_phone"

    await m.answer("Введи номер телефону для зв'язку:", reply_markup=phone_menu())


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def tutor_contact(m: types.Message):
    state = user_state.get(m.from_user.id)
    if state != "tutor_phone":
        return

    phone = m.contact.phone_number
    user_temp[m.from_user.id]["phone"] = phone
    user_state[m.from_user.id] = "tutor_level"

    await m.answer("Вкажи свій рівень або клас:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_phone")
async def tutor_phone(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "tutor_name"
        await m.answer("Введи своє ім'я:", reply_markup=back())
        return

    phone = m.text.strip()

    if len(phone) < 6:
        await m.answer("❌ Будь ласка, введи коректний номер телефону або натисни кнопку.", reply_markup=phone_menu())
        return

    user_temp[m.from_user.id]["phone"] = phone
    user_state[m.from_user.id] = "tutor_level"

    await m.answer("Вкажи свій рівень або клас:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_level")
async def tutor_level(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "tutor_phone"
        await m.answer("Введи номер телефону для зв'язку:", reply_markup=phone_menu())
        return

    user_temp[m.from_user.id]["level"] = m.text.strip()
    user_state[m.from_user.id] = "tutor_goal"

    await m.answer("Напиши коротко свою ціль або проблему:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_goal")
async def tutor_goal(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "tutor_level"
        await m.answer("Вкажи свій рівень або клас:", reply_markup=back())
        return

    user_temp[m.from_user.id]["goal"] = m.text.strip()
    user_state[m.from_user.id] = "tutor_time"

    await m.answer("Напиши зручний час для занять:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_time")
async def tutor_time(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "tutor_goal"
        await m.answer("Напиши коротко свою ціль або проблему:", reply_markup=back())
        return

    user_temp[m.from_user.id]["time"] = m.text.strip()
    user_state[m.from_user.id] = "tutor_format"

    await m.answer("Вкажи формат: онлайн / офлайн:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_format")
async def tutor_format(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "tutor_time"
        await m.answer("Напиши зручний час для занять:", reply_markup=back())
        return

    user_temp[m.from_user.id]["format"] = m.text.strip()
    user_state[m.from_user.id] = "tutor_confirm"

    d = user_temp[m.from_user.id]
    text = (
        "Перевір дані заявки перед відправкою:\n\n"
        f"Категорія: {d.get('category', '-')}\n"
        f"Предмет: {d.get('subject', '-')}\n"
        f"Ім'я: {d.get('name', '-')}\n"
        f"Телефон: {d.get('phone', '-')}\n"
        f"Рівень / клас: {d.get('level', '-')}\n"
        f"Ціль / проблема: {d.get('goal', '-')}\n"
        f"Зручний час: {d.get('time', '-')}\n"
        f"Формат: {d.get('format', '-')}"
    )

    await m.answer(text, reply_markup=confirm_request_menu())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "tutor_confirm")
async def tutor_confirm(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "tutor_format"
        await m.answer("Вкажи формат: онлайн / офлайн:", reply_markup=back())
        return

    if m.text == "✏️ Редагувати":
        user_state[m.from_user.id] = "tutor_name"
        await m.answer("Введи своє ім'я:", reply_markup=back())
        return

    if m.text != "✅ Підтвердити":
        await m.answer("Натисни кнопку для підтвердження або редагування.", reply_markup=confirm_request_menu())
        return

    d = user_temp.get(m.from_user.id, {})
    request_id = save_tutor_request(
        user_id=m.from_user.id,
        category=d.get("category", ""),
        subject=d.get("subject", ""),
        client_name=d.get("name", ""),
        phone=d.get("phone", ""),
        level=d.get("level", ""),
        goal=d.get("goal", ""),
        preferred_time=d.get("time", ""),
        lesson_format=d.get("format", "")
    )

    admin_text = (
        f"📚 Нова заявка на репетитора\n"
        f"Заявка #{request_id}\n"
        f"ID: {m.from_user.id}\n"
        f"Категорія: {d.get('category', '-')}\n"
        f"Предмет: {d.get('subject', '-')}\n"
        f"Ім'я: {d.get('name', '-')}\n"
        f"Телефон: {d.get('phone', '-')}\n"
        f"Рівень / клас: {d.get('level', '-')}\n"
        f"Ціль / проблема: {d.get('goal', '-')}\n"
        f"Зручний час: {d.get('time', '-')}\n"
        f"Формат: {d.get('format', '-')}\n"
        f"Статус: new"
    )

    if m.from_user.username:
        admin_text += f"\nUsername: @{m.from_user.username}"

    if is_premium(m.from_user.id):
        conn = db()
        cur = conn.cursor()
        cur.execute("SELECT premium_until FROM users WHERE user_id=?", (m.from_user.id,))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            admin_text += f"\nПрофіль: Преміум до {row[0][:16]}"
    else:
        admin_text += "\nПрофіль: Базовий"

    for admin_id in get_admins():
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception as e:
            logging.warning(f"Не вдалося надіслати заявку адміну {admin_id}: {e}")

    await m.answer("✅ Заявку створено.", reply_markup=main_menu())
    user_state[m.from_user.id] = "main"
    user_temp.pop(m.from_user.id, None)


# ---------------- СКАРГИ ТА ПІДТРИМКА ----------------

@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "complaint")
async def complaint_text(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "main"
        await m.answer("👋 Обери дію", reply_markup=main_menu())
        return

    premium_status = "Преміум" if is_premium(m.from_user.id) else "Базовий"

    text = (
        f"⚠️ Нова скарга\n"
        f"ID: {m.from_user.id}\n"
        f"Профіль: {premium_status}\n"
        f"Текст: {m.text}"
    )

    if m.from_user.username:
        text += f"\nUsername: @{m.from_user.username}"

    for admin_id in get_admins():
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            logging.warning(f"Не вдалося надіслати скаргу адміну {admin_id}: {e}")

    await m.answer("✅ Скаргу відправлено адміністраторам.", reply_markup=main_menu())
    user_state[m.from_user.id] = "main"


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "support")
async def support_text(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "main"
        await m.answer("👋 Обери дію", reply_markup=main_menu())
        return

    text = (
        f"🆘 Повідомлення в підтримку\n"
        f"ID: {m.from_user.id}\n"
        f"Текст: {m.text}"
    )

    if m.from_user.username:
        text += f"\nUsername: @{m.from_user.username}"

    for admin_id in get_admins():
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            logging.warning(f"Не вдалося надіслати support адміну {admin_id}: {e}")

    await m.answer("✅ Повідомлення в підтримку відправлено.", reply_markup=main_menu())
    user_state[m.from_user.id] = "main"


# ---------------- АДМІН-ПАНЕЛЬ ----------------

@dp.message_handler(lambda m: m.text == "🔐 Вхід адміністратора")
async def admin_login_btn(m: types.Message):
    user_state[m.from_user.id] = "admin_login_step_1"
    await m.answer("Введи логін адміністратора:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "admin_login_step_1")
async def admin_login_step_1(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "main"
        await m.answer("👋 Обери дію", reply_markup=main_menu())
        return

    user_temp[m.from_user.id] = {"admin_login": m.text.strip()}
    user_state[m.from_user.id] = "admin_login_step_2"
    await m.answer("Введи пароль адміністратора:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "admin_login_step_2")
async def admin_login_step_2(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "admin_login_step_1"
        await m.answer("Введи логін адміністратора:", reply_markup=back())
        return

    login_value = user_temp.get(m.from_user.id, {}).get("admin_login", "")
    password_value = m.text.strip()

    if login_value == os.getenv("ADMIN_LOGIN", "admin") and password_value == os.getenv("ADMIN_PASSWORD", "123456"):
        add_admin(m.from_user.id)
        await m.answer("✅ Вхід адміністратора успішний.", reply_markup=admin_menu())
        user_state[m.from_user.id] = "admin_panel"
    else:
        await m.answer("❌ Невірний логін або пароль.", reply_markup=main_menu())
        user_state[m.from_user.id] = "main"

    user_temp.pop(m.from_user.id, None)


@dp.message_handler(lambda m: m.text == "📥 Нові заявки")
async def admin_new_requests(m: types.Message):
    if m.from_user.id not in get_admins():
        return

    rows = get_new_requests()

    if not rows:
        await m.answer("Немає нових заявок.", reply_markup=admin_menu())
        return

    lines = ["📥 Нові заявки:\n"]
    for r in rows[:20]:
        lines.append(f"#{r[0]} | user {r[1]} | {r[2]} | {r[3]} | {r[4]}")

    await m.answer("\n".join(lines), reply_markup=admin_menu())


@dp.message_handler(lambda m: m.text == "💎 Преміум-користувачі")
async def admin_premium_users(m: types.Message):
    if m.from_user.id not in get_admins():
        return

    rows = get_premium_users()

    if not rows:
        await m.answer("Немає активних преміум-користувачів.", reply_markup=admin_menu())
        return

    lines = ["💎 Преміум-користувачі:\n"]
    for user_id, premium_until in rows[:50]:
        lines.append(f"{user_id} — до {premium_until[:16]}")

    await m.answer("\n".join(lines), reply_markup=admin_menu())


@dp.message_handler(lambda m: m.text == "🔎 Пошук")
async def admin_search_btn(m: types.Message):
    if m.from_user.id not in get_admins():
        return

    user_state[m.from_user.id] = "admin_search"
    await m.answer("Введи ID користувача:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "admin_search")
async def admin_search(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "admin_panel"
        await m.answer("🛠 Адмін-панель", reply_markup=admin_menu())
        return

    if not m.text.isdigit():
        await m.answer("Введи тільки числовий ID.", reply_markup=back())
        return

    user_id = int(m.text)

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
    user_row = cur.fetchone()

    cur.execute("SELECT subject, status, created_at FROM tutor_requests WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    reqs = cur.fetchall()

    cur.execute("SELECT type, amount, created FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    pays = cur.fetchall()
    conn.close()

    premium_info = "Базовий профіль"
    if user_row and user_row[0]:
        premium_info = f"Преміум до {user_row[0][:16]}"

    lines = [f"🔎 Користувач {user_id}", premium_info, ""]

    lines.append("📂 Заявки:")
    if reqs:
        for r in reqs:
            lines.append(f"• {r[0]} | {r[1]} | {r[2][:16]}")
    else:
        lines.append("• Немає")

    lines.append("")
    lines.append("💳 Оплати:")
    if pays:
        for p in pays:
            lines.append(f"• {p[0]} | {p[1]}⭐ | {p[2][:16]}")
    else:
        lines.append("• Немає")

    await m.answer("\n".join(lines), reply_markup=admin_menu())
    user_state[m.from_user.id] = "admin_panel"


@dp.message_handler(lambda m: m.text == "💬 Відповісти клієнту")
async def admin_reply_btn(m: types.Message):
    if m.from_user.id not in get_admins():
        return

    user_state[m.from_user.id] = "admin_reply_user_id"
    await m.answer("Введи ID користувача, якому хочеш відповісти:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "admin_reply_user_id")
async def admin_reply_user_id(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "admin_panel"
        await m.answer("🛠 Адмін-панель", reply_markup=admin_menu())
        return

    if not m.text.isdigit():
        await m.answer("Введи тільки числовий ID.", reply_markup=back())
        return

    user_temp[m.from_user.id] = {"reply_user_id": int(m.text)}
    user_state[m.from_user.id] = "admin_reply_text"
    await m.answer("Введи текст відповіді для користувача:", reply_markup=back())


@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "admin_reply_text")
async def admin_reply_text(m: types.Message):
    if m.text == "⬅️ Назад":
        user_state[m.from_user.id] = "admin_reply_user_id"
        await m.answer("Введи ID користувача, якому хочеш відповісти:", reply_markup=back())
        return

    target_user_id = user_temp.get(m.from_user.id, {}).get("reply_user_id")
    if not target_user_id:
        await m.answer("Помилка. Спробуй ще раз.", reply_markup=admin_menu())
        user_state[m.from_user.id] = "admin_panel"
        return

    try:
        await bot.send_message(target_user_id, f"💬 Повідомлення від адміністратора:\n\n{m.text}")
        await m.answer("✅ Повідомлення користувачу відправлено.", reply_markup=admin_menu())
    except Exception as e:
        await m.answer(f"❌ Не вдалося відправити повідомлення: {e}", reply_markup=admin_menu())

    user_temp.pop(m.from_user.id, None)
    user_state[m.from_user.id] = "admin_panel"


# ---------------- ЗАГАЛЬНІ КНОПКИ ----------------

@dp.message_handler(lambda m: m.text == "Виконати завдання🙏")
async def task_menu_open(m: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Одне завдання")
    kb.row("Комплексне виконання роботи")
    kb.row("Преміум профіль")
    kb.row("⬅️ Назад")
    await m.answer("👇 Обери послугу", reply_markup=kb)


@dp.message_handler(lambda m: m.text == "📋 Меню")
async def open_menu(m: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("👤 Моя анкета")
    kb.row("⭐ Premium")
    kb.row("🚫 Поскаржитися")
    kb.row("🌍 Мова")
    if m.from_user.id in get_admins():
        kb.row("🛠 Адмін-панель")
    else:
        kb.row("🔐 Вхід адміністратора")
    kb.row("⬅️ Назад")
    await m.answer("📋 Меню", reply_markup=kb)


@dp.message_handler(lambda m: m.text == "👤 Моя анкета")
async def profile_button(m: types.Message):
    await myprofile_cmd(m)


@dp.message_handler(lambda m: m.text == "⭐ Premium")
async def premium_button(m: types.Message):
    await premium_cmd(m)


@dp.message_handler(lambda m: m.text == "🚫 Поскаржитися")
async def complaint_button(m: types.Message):
    await complaint_cmd(m)


@dp.message_handler(lambda m: m.text == "🌍 Мова")
async def language_button(m: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🇺🇦 Українська", "🇷🇺 Русский")
    kb.row("🇬🇧 English", "🇩🇪 Deutsch")
    kb.row("🇫🇷 Français", "🇮🇹 Italiano")
    kb.row("🇪🇸 Español", "🇫🇮 Suomi")
    kb.row("⬅️ Назад")
    await m.answer("👋 Вибери мову бота", reply_markup=kb)


@dp.message_handler(lambda m: m.text == "🛠 Адмін-панель")
async def admin_panel_btn(m: types.Message):
    if m.from_user.id not in get_admins():
        return
    user_state[m.from_user.id] = "admin_panel"
    await m.answer("🛠 Адмін-панель", reply_markup=admin_menu())


@dp.message_handler(lambda m: m.text in ["🇺🇦 Українська", "🇷🇺 Русский", "🇬🇧 English", "🇩🇪 Deutsch", "🇫🇷 Français", "🇮🇹 Italiano", "🇪🇸 Español", "🇫🇮 Suomi"])
async def change_language_simple(m: types.Message):
    lang_map = {
        "🇺🇦 Українська": "ua",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
        "🇩🇪 Deutsch": "de",
        "🇫🇷 Français": "fr",
        "🇮🇹 Italiano": "it",
        "🇪🇸 Español": "es",
        "🇫🇮 Suomi": "fi",
    }
    lang = lang_map[m.text]

    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, premium_until) VALUES (?, NULL)", (m.from_user.id,))
    cur.execute("ALTER TABLE users ADD COLUMN language TEXT", ())
    conn.commit()
    conn.close()

@dp.message_handler(lambda m: m.text in ["🇺🇦 Українська", "🇷🇺 Русский", "🇬🇧 English", "🇩🇪 Deutsch", "🇫🇷 Français", "🇮🇹 Italiano", "🇪🇸 Español", "🇫🇮 Suomi"])
async def set_language_final(m: types.Message):
    lang_map = {
        "🇺🇦 Українська": "ua",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
        "🇩🇪 Deutsch": "de",
        "🇫🇷 Français": "fr",
        "🇮🇹 Italiano": "it",
        "🇪🇸 Español": "es",
        "🇫🇮 Suomi": "fi",
    }

    selected = lang_map[m.text]

    conn = db()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET premium_until = premium_until WHERE user_id=?", (m.from_user.id,))
    except:
        pass

    try:
        cur.execute("ALTER TABLE users ADD COLUMN language TEXT")
    except:
        pass

    cur.execute("INSERT OR IGNORE INTO users (user_id, premium_until, language) VALUES (?, NULL, ?)", (m.from_user.id, selected))
    cur.execute("UPDATE users SET language=? WHERE user_id=?", (selected, m.from_user.id))
    conn.commit()
    conn.close()

    await m.answer("✅ Мову змінено.", reply_markup=main_menu())


@dp.message_handler(lambda m: m.text == "⬅️ Назад")
async def back_handler(m: types.Message):
    user_state[m.from_user.id] = "main"
    await m.answer("👋 Обери дію", reply_markup=main_menu())


# ---------------- ЗАПУСК ----------------

async def on_startup(_):
    init_db()
    add_admin(OWNER_ID)
    await bot.set_my_commands([
        BotCommand("myprofile", "Моя анкета"),
        BotCommand("premium", "Premium"),
        BotCommand("complaint", "Поскаржитися"),
    ])

    try:
        await check_premium_reminders()
    except Exception as e:
        logging.warning(f"Помилка перевірки преміум-нагадувань: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)