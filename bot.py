import logging
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils import executor

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "510644962"))
ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")
DB_PATH = os.getenv("DB_PATH", "bot.db")
BOT_USERNAME = ""
TOP_UP_AMOUNT_OPTIONS = [100, 250, 500, 1000, 2500]
REFERRAL_REWARD_STARS = 250

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
        "start_phone_request": "📱 Для початку користування ботом поділись своїм номером телефону Telegram.",
        "start_phone_saved": "✅ Номер телефону збережено.",

        "task": "Виконати завдання🙏",
        "tutor": "Потрібен репетитор💪",
        "my_requests_btn": "📂 Мої заявки",
        "support_btn": "🆘 Підтримка",
        "menu_btn": "👤 Мій акаунт",
        "back": "🏠 Початкове меню",

        "one": "Одне завдання",
        "complex": "Комплексне виконання роботи",
        "premium_profile": "Premium профіль",
        "premium_profile_info": "Увесь місяць тобі доступна необмежена кількість завдань з будь якого шкільного предмету",
        "profile_upgrade_btn": "🚀 Прокачати профіль до Premium рівня",
        "choose_service": "👇 Обери послугу",

        "file_sent": "📩 Файл відправлено адміністратору.",
        "file_sent_to_tutor": "📩 Файл відправлено Tutor.",
        "no_payment": "❌ Спочатку потрібно оплатити.",
        "send_file_now": "📎 Тепер можеш надіслати файл.",
        "pay_success_task": "✅ Оплата 250⭐ пройшла успішно.",
        "pay_success_complex": "✅ Оплата 500⭐ пройшла успішно.",
        "pay_success_premium_profile": "✅ Оплата 2500⭐ за преміум профіль пройшла успішно.",
        "premium_profile_activated": "💎 Преміум профіль активовано на 30 днів.",

        "system_menu_title": "👤 Мій акаунт",
        "my_profile_btn": "👤 Моя анкета",
        "premium_menu_btn": "⭐ Premium профіль",
        "tutor_login_btn": "🎓 Вхід в Tutor акаунт",
        "tutor_profile_btn": "📚 Tutor профіль",
        "tutor_logout_btn": "🚪 Вихід з Tutor-профіля",
        "tutor_logout_success": "✅ Ти вийшов з Tutor-профіля.",
        "admin_login_btn": "🔐 Вхід в Admin акаунт",
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
        "profile_tutor": "Tutor",
        "profile_basic": "Базовий профіль",
        "profile_premium": "Преміум профіль",
        "payments_history_title": "💳 Історія оплат",
        "orders_history_title": "📦 Історія заявок",
        "no_payments_history": "Історія оплат поки порожня.",
        "no_requests": "У тебе ще немає заявок.",
        "change_language_btn": "🌍 Змінити мову",

        "complaint_sent": "✅ Повідомлення відправлено адміністратору.",
        "complaint_header": "🆘 Нове повідомлення",
        "complaint_user_id": "ID користувача",
        "complaint_username": "Username",
        "complaint_language": "Мова",
        "complaint_profile": "Профіль",
        "complaint_text_label": "Текст",

        "support_text": "🆘 Напиши своє питання одним повідомленням, і адміністратор отримає його.",

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

        "tutor_auth_success": "✅ Вхід Tutor успішний.",
        "tutor_register_success": "✅ Tutor-профіль створено. Вхід виконано.",
        "tutor_panel_title": "📚 Tutor-панель",
        "tutor_panel_name": "👤 Tutor",
        "tutor_panel_balance": "💰 Баланс",
        "tutor_panel_withdraw_status_ready": "✅ Виведення доступне",
        "tutor_panel_withdraw_status_wait": "⏳ Для виведення потрібно ще {remaining}⭐",
        "tutor_new_requests_btn": "🆕 Нові заявки",
        "tutor_my_requests_btn": "📂 Заявки в роботі",
        "tutor_no_new_requests": "Немає нових заявок для Tutor.",
        "tutor_no_my_requests": "У тебе ще немає заявок у роботі.",
        "tutor_take_request_btn": "✅ Взяти в роботу",
        "tutor_take_success": "✅ Заявку взято в роботу.",
        "tutor_take_failed": "⚠️ Цю заявку вже взяв інший Tutor.",
        "tutor_request_taken_user": "✅ Твою заявку взяв Tutor. Він може написати тобі тут у чат.",
        "tutor_request_detail_title": "📄 Заявка",
        "tutor_write_user_btn": "💬 Написати користувачу",
        "tutor_send_file_btn": "📎 Надіслати файл користувачу",
        "tutor_reply_text_prompt": "Введи повідомлення для користувача:",
        "tutor_reply_text_sent": "✅ Повідомлення користувачу надіслано.",
        "tutor_send_file_prompt": "Надішли файл для користувача одним повідомленням.",
        "tutor_send_file_sent": "✅ Файл користувачу надіслано.",
        "request_files_title": "📎 Файли по заявці",
        "no_request_files": "Файлів по цій заявці поки немає.",
        "file_from_user_caption": "📎 Файл від користувача по заявці",
        "file_from_tutor_caption": "📎 Файл від Tutor по заявці",

        "tutor_balance_label": "Баланс",
        "tutor_withdraw_btn": "💸 Виведення коштів",
        "tutor_enter_card": "Введи номер картки для виведення коштів:",
        "tutor_withdraw_sent": "✅ Запит на виведення коштів відправлено адміністратору.",
        "tutor_withdraw_not_available": "❌ Виведення можливе лише коли баланс досягне 1000⭐.",
        "tutor_withdraw_balance_info": "💰 Поточний баланс: {balance}⭐",
        "tutor_withdraw_request_title": "💸 Tutor хоче вивести кошти",
        "card_number_label": "Номер картки",

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
        "start_phone_request": "📱 Для начала пользования ботом поделись своим номером телефона Telegram.",
        "start_phone_saved": "✅ Номер телефона сохранён.",

        "task": "Выполнить задание🙏",
        "tutor": "Нужен репетитор💪",
        "my_requests_btn": "📂 Мои заявки",
        "support_btn": "🆘 Поддержка",
        "menu_btn": "👤 Мой аккаунт",
        "back": "🏠 Главное меню",

        "one": "Одно задание",
        "complex": "Комплексное выполнение работы",
        "premium_profile": "Premium профиль",
        "premium_profile_info": "Весь месяц тебе доступно неограниченное количество заданий по любому школьному предмету",
        "profile_upgrade_btn": "🚀 Прокачать профиль до Premium уровня",
        "choose_service": "👇 Выберите услугу",

        "file_sent": "📩 Файл отправлен администратору.",
        "file_sent_to_tutor": "📩 Файл отправлен Tutor.",
        "no_payment": "❌ Сначала нужно оплатить.",
        "send_file_now": "📎 Теперь можешь отправить файл.",
        "pay_success_task": "✅ Оплата 250⭐ прошла успешно.",
        "pay_success_complex": "✅ Оплата 500⭐ прошла успешно.",
        "pay_success_premium_profile": "✅ Оплата 2500⭐ за премиум профиль прошла успешно.",
        "premium_profile_activated": "💎 Премиум профиль активирован на 30 дней.",

        "system_menu_title": "👤 Мой аккаунт",
        "my_profile_btn": "👤 Моя анкета",
        "premium_menu_btn": "⭐ Premium профиль",
        "tutor_login_btn": "🎓 Вход в Tutor аккаунт",
        "tutor_profile_btn": "📚 Tutor профиль",
        "tutor_logout_btn": "🚪 Выход из Tutor-профиля",
        "tutor_logout_success": "✅ Ты вышел из Tutor-профиля.",
        "admin_login_btn": "🔐 Вход в Admin аккаунт",
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
        "profile_tutor": "Tutor",
        "profile_basic": "Базовый профиль",
        "profile_premium": "Премиум профиль",
        "payments_history_title": "💳 История оплат",
        "orders_history_title": "📦 История заявок",
        "no_payments_history": "История оплат пока пуста.",
        "no_requests": "У тебя ещё нет заявок.",
        "change_language_btn": "🌍 Изменить язык",

        "complaint_sent": "✅ Сообщение отправлено администратору.",
        "complaint_header": "🆘 Новое сообщение",
        "complaint_user_id": "ID пользователя",
        "complaint_username": "Username",
        "complaint_language": "Язык",
        "complaint_profile": "Профиль",
        "complaint_text_label": "Текст",

        "support_text": "🆘 Напиши свой вопрос одним сообщением, и администратор его получит.",

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

        "tutor_auth_success": "✅ Вход Tutor успешный.",
        "tutor_register_success": "✅ Tutor-профиль создан. Вход выполнен.",
        "tutor_panel_title": "📚 Tutor-панель",
        "tutor_panel_name": "👤 Tutor",
        "tutor_panel_balance": "💰 Баланс",
        "tutor_panel_withdraw_status_ready": "✅ Вывод доступен",
        "tutor_panel_withdraw_status_wait": "⏳ Для вывода нужно ещё {remaining}⭐",
        "tutor_new_requests_btn": "🆕 Новые заявки",
        "tutor_my_requests_btn": "📂 Заявки в работе",
        "tutor_no_new_requests": "Нет новых заявок для Tutor.",
        "tutor_no_my_requests": "У тебя ещё нет заявок в работе.",
        "tutor_take_request_btn": "✅ Взять в работу",
        "tutor_take_success": "✅ Заявка взята в работу.",
        "tutor_take_failed": "⚠️ Эту заявку уже взял другой Tutor.",
        "tutor_request_taken_user": "✅ Твою заявку взял Tutor. Он может написать тебе здесь в чат.",
        "tutor_request_detail_title": "📄 Заявка",
        "tutor_write_user_btn": "💬 Написать пользователю",
        "tutor_send_file_btn": "📎 Отправить файл пользователю",
        "tutor_reply_text_prompt": "Введи сообщение для пользователя:",
        "tutor_reply_text_sent": "✅ Сообщение пользователю отправлено.",
        "tutor_send_file_prompt": "Отправь файл для пользователя одним сообщением.",
        "tutor_send_file_sent": "✅ Файл пользователю отправлен.",
        "request_files_title": "📎 Файлы по заявке",
        "no_request_files": "Файлов по этой заявке пока нет.",
        "file_from_user_caption": "📎 Файл от пользователя по заявке",
        "file_from_tutor_caption": "📎 Файл от Tutor по заявке",

        "tutor_balance_label": "Баланс",
        "tutor_withdraw_btn": "💸 Вывод средств",
        "tutor_enter_card": "Введи номер карты для вывода средств:",
        "tutor_withdraw_sent": "✅ Запрос на вывод средств отправлен администратору.",
        "tutor_withdraw_not_available": "❌ Вывод возможен только когда баланс достигнет 1000⭐.",
        "tutor_withdraw_balance_info": "💰 Текущий баланс: {balance}⭐",
        "tutor_withdraw_request_title": "💸 Tutor хочет вывести средства",
        "card_number_label": "Номер карты",

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
        "no_access": "⛔ Нет доступа.",
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

TEXTS["ua"].update({
    "share_phone_btn": "📱 Поділитися номером",
    "balance_label": "Баланс",
    "balance_top_up_btn": "💳 Поповнити баланс",
    "balance_top_up_title": "💳 Обери суму поповнення балансу:",
    "balance_top_up_invoice_title": "Поповнення балансу",
    "balance_top_up_invoice_description": "Поповнення внутрішнього балансу бота",
    "balance_top_up_success": "✅ Баланс успішно поповнено на {amount}⭐.",
    "balance_history_top_up": "Поповнення балансу",
    "referral_link_btn": "🔗 Реферальне посилання",
    "referral_link_text": "За кожного користувача, який доєднається до бота за твоїм посиланням тобі буде нараховано 250 зірочок, які ти зможеш витратити для оплати послуг",
    "referral_link_unavailable": "❌ Не вдалося сформувати реферальне посилання. Спробуй ще раз пізніше.",
    "referral_reward_received": "🎉 За твоїм реферальним посиланням зареєструвався новий користувач. Тобі нараховано 250⭐.",
    "admin_balance_btn": "⭐ Змінити баланс",
    "admin_balance_lookup_prompt": "Введи ID, username або номер телефону користувача:",
    "admin_balance_amount_prompt": "Введи зміну балансу у зірочках. Приклади: 250, -250 або =1000",
    "admin_balance_user_found": "Користувача знайдено",
    "admin_balance_changed": "✅ Баланс користувача оновлено.",
    "admin_balance_notification": "💬 Адміністратор змінив твій баланс на {amount}⭐. Поточний баланс: {balance}⭐",
    "admin_balance_user_not_found": "❌ Користувача не знайдено за цими даними.",
    "admin_balance_invalid_amount": "❌ Некоректне значення. Введи 250, -250 або =1000",
    "admin_balance_current": "Поточний баланс",
    "telegram_username_label": "Username",
    "referrer_label": "Запросив",
})

TEXTS["ru"].update({
    "share_phone_btn": "📱 Поделиться номером",
    "balance_label": "Баланс",
    "balance_top_up_btn": "💳 Пополнить баланс",
    "balance_top_up_title": "💳 Выбери сумму пополнения баланса:",
    "balance_top_up_invoice_title": "Пополнение баланса",
    "balance_top_up_invoice_description": "Пополнение внутреннего баланса бота",
    "balance_top_up_success": "✅ Баланс успешно пополнен на {amount}⭐.",
    "balance_history_top_up": "Пополнение баланса",
    "referral_link_btn": "🔗 Реферальная ссылка",
    "referral_link_text": "За каждого пользователя, который присоединится к боту по твоей ссылке тебе будет начислено 250 звёздочек, которые ты сможешь потратить на оплату услуг",
    "referral_link_unavailable": "❌ Не удалось сформировать реферальную ссылку. Попробуй ещё раз позже.",
    "referral_reward_received": "🎉 По твоей реферальной ссылке зарегистрировался новый пользователь. Тебе начислено 250⭐.",
    "admin_balance_btn": "⭐ Изменить баланс",
    "admin_balance_lookup_prompt": "Введи ID, username или номер телефона пользователя:",
    "admin_balance_amount_prompt": "Введи изменение баланса в звёздочках. Примеры: 250, -250 или =1000",
    "admin_balance_user_found": "Пользователь найден",
    "admin_balance_changed": "✅ Баланс пользователя обновлён.",
    "admin_balance_notification": "💬 Администратор изменил твой баланс на {amount}⭐. Текущий баланс: {balance}⭐",
    "admin_balance_user_not_found": "❌ Пользователь не найден по этим данным.",
    "admin_balance_invalid_amount": "❌ Некорректное значение. Введи 250, -250 или =1000",
    "admin_balance_current": "Текущий баланс",
    "telegram_username_label": "Username",
    "referrer_label": "Пригласил",
})

def get_telegram_full_name(user: types.User | None) -> str:
    if not user:
        return ""
    parts = [user.first_name or "", user.last_name or ""]
    full_name = " ".join(part.strip() for part in parts if part and part.strip()).strip()
    return full_name or (user.username or "")


def db():
    return sqlite3.connect(DB_PATH)


def column_exists(cur, table_name: str, column_name: str) -> bool:
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cur.fetchall()]
    return column_name in columns


def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    value = phone.strip()
    has_plus = value.startswith("+")
    digits = re.sub(r"\D", "", value)
    if not digits:
        return ""
    return f"+{digits}" if has_plus else digits


def normalize_username(username: str) -> str:
    value = (username or "").strip()
    if value.startswith("@"):
        value = value[1:]
    return value.lower()


def user_exists(user_id: int) -> bool:
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row)


def get_bot_referral_link(user_id: int) -> str:
    if not BOT_USERNAME:
        return ""
    return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"


def get_start_referrer_id(message: types.Message):
    args = (message.get_args() or "").strip()
    if not args.startswith("ref_"):
        return None
    value = args[4:].strip()
    if not value.isdigit():
        return None
    return int(value)


def referral_already_recorded(referred_user_id: int) -> bool:
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM referrals WHERE referred_user_id = ?", (referred_user_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row)


def award_referral_bonus(referrer_user_id: int, referred_user_id: int) -> bool:
    if not referrer_user_id or referrer_user_id == referred_user_id:
        return False
    if referral_already_recorded(referred_user_id):
        return False

    ensure_user(referrer_user_id)
    ensure_user(referred_user_id)

    conn = db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO referrals (referrer_user_id, referred_user_id, reward_stars, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (referrer_user_id, referred_user_id, REFERRAL_REWARD_STARS, datetime.now(timezone.utc).isoformat())
    )
    inserted = cur.rowcount > 0
    conn.commit()
    conn.close()

    if not inserted:
        return False

    add_user_balance(referrer_user_id, REFERRAL_REWARD_STARS, note=f"Referral reward for user #{referred_user_id}")
    return True


def get_referrer_for_user(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT referrer_user_id FROM referrals WHERE referred_user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def set_user_username(user_id: int, username: str | None):
    ensure_user(user_id)
    normalized = normalize_username(username or "")
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET telegram_username = ? WHERE user_id = ?", (normalized or None, user_id))
    conn.commit()
    conn.close()


def find_user_id_by_identifier(identifier: str):
    value = (identifier or "").strip()
    if not value:
        return None

    conn = db()
    cur = conn.cursor()

    if value.isdigit():
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (int(value),))
        row = cur.fetchone()
        if row:
            conn.close()
            return row[0]

    normalized_phone = normalize_phone(value)
    if normalized_phone:
        cur.execute("SELECT user_id FROM users WHERE phone = ?", (normalized_phone,))
        row = cur.fetchone()
        if row:
            conn.close()
            return row[0]

    username = normalize_username(value)
    if username:
        cur.execute("SELECT user_id FROM users WHERE lower(COALESCE(telegram_username, '')) = ?", (username,))
        row = cur.fetchone()
        if row:
            conn.close()
            return row[0]

    conn.close()
    return None


def set_user_balance(user_id: int, new_balance: int):
    ensure_user(user_id)
    new_balance = max(0, int(new_balance))
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET user_balance_stars = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()
    return new_balance


def parse_balance_change_input(text_value: str):
    value = (text_value or "").strip().replace(" ", "")
    if not value:
        return None
    if value.startswith("="):
        target = value[1:]
        if target.lstrip("-").isdigit():
            return ("set", int(target))
        return None
    if value.lstrip("+-").isdigit():
        return ("delta", int(value))
    return None


def get_user_balance(user_id: int) -> int:
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT user_balance_stars FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return int(row[0] or 0) if row else 0


def add_user_balance(user_id: int, amount_stars: int, note: str = "") -> int:
    ensure_user(user_id)
    amount_stars = int(amount_stars)
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(user_balance_stars, 0) FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    current_balance = int(row[0] or 0) if row else 0
    new_balance = max(0, current_balance + amount_stars)
    cur.execute("UPDATE users SET user_balance_stars = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()
    return new_balance


def get_payment_label(payment_type: str, lang: str) -> str:
    labels = {
        "task": TEXTS[lang].get("one", "task"),
        "complex": TEXTS[lang].get("complex", "complex"),
        "premium_profile": TEXTS[lang].get("premium_profile", "premium_profile"),
        "balance_top_up": TEXTS[lang].get("balance_history_top_up", "Balance top up"),
    }
    return labels.get(payment_type, payment_type)


def get_tutor_withdraw_progress(tutor_user_id: int) -> tuple[int, int, int]:
    balance = get_tutor_balance(tutor_user_id)
    target = 1000
    remaining = max(0, target - balance)
    return balance, target, remaining


def get_tutor_withdraw_button_text(tutor_user_id: int, lang: str) -> str:
    balance, target, _ = get_tutor_withdraw_progress(tutor_user_id)
    return f"{TEXTS[lang]['tutor_withdraw_btn']} {balance}/{target}⭐"


def is_tutor_withdraw_button_text(text_value: str, tutor_user_id: int, lang: str) -> bool:
    return text_value == TEXTS[lang]['tutor_withdraw_btn'] or text_value == get_tutor_withdraw_button_text(tutor_user_id, lang)


def build_tutor_balance_info_text(tutor_user_id: int, lang: str) -> str:
    balance, target, remaining = get_tutor_withdraw_progress(tutor_user_id)
    if remaining > 0:
        if lang == "ua":
            return f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\nДо виведення залишилось заробити: {remaining}⭐"
        return f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\nДо вывода осталось заработать: {remaining}⭐"
    if lang == "ua":
        return f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\nВиведення вже доступне."
    return f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\nВывод уже доступен."

def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'ua',
            manual_language INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            is_tutor INTEGER DEFAULT 0,
            phone TEXT,
            full_name TEXT,
            telegram_username TEXT,
            user_balance_stars INTEGER DEFAULT 0,
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
        CREATE TABLE IF NOT EXISTS tutor_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
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
            created_at TEXT NOT NULL,
            assigned_tutor_id INTEGER,
            payment_type TEXT,
            payment_amount_stars INTEGER DEFAULT 0,
            payment_awarded_to_tutor INTEGER DEFAULT 0,
            paid_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS request_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            sender_user_id INTEGER NOT NULL,
            sender_role TEXT NOT NULL,
            file_id TEXT NOT NULL,
            file_name TEXT,
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_user_id INTEGER NOT NULL,
            referred_user_id INTEGER NOT NULL UNIQUE,
            reward_stars INTEGER NOT NULL DEFAULT 250,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tutor_balances (
            tutor_user_id INTEGER PRIMARY KEY,
            balance_stars INTEGER NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tutor_balance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutor_user_id INTEGER NOT NULL,
            request_id INTEGER,
            amount_stars INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
    """)

    if not column_exists(cur, "users", "is_tutor"):
        cur.execute("ALTER TABLE users ADD COLUMN is_tutor INTEGER DEFAULT 0")

    if not column_exists(cur, "users", "phone"):
        cur.execute("ALTER TABLE users ADD COLUMN phone TEXT")

    if not column_exists(cur, "users", "full_name"):
        cur.execute("ALTER TABLE users ADD COLUMN full_name TEXT")

    if not column_exists(cur, "users", "telegram_username"):
        cur.execute("ALTER TABLE users ADD COLUMN telegram_username TEXT")

    if not column_exists(cur, "users", "user_balance_stars"):
        cur.execute("ALTER TABLE users ADD COLUMN user_balance_stars INTEGER DEFAULT 0")

    if not column_exists(cur, "tutor_requests", "assigned_tutor_id"):
        cur.execute("ALTER TABLE tutor_requests ADD COLUMN assigned_tutor_id INTEGER")

    if not column_exists(cur, "tutor_requests", "payment_type"):
        cur.execute("ALTER TABLE tutor_requests ADD COLUMN payment_type TEXT")

    if not column_exists(cur, "tutor_requests", "payment_amount_stars"):
        cur.execute("ALTER TABLE tutor_requests ADD COLUMN payment_amount_stars INTEGER DEFAULT 0")

    if not column_exists(cur, "tutor_requests", "payment_awarded_to_tutor"):
        cur.execute("ALTER TABLE tutor_requests ADD COLUMN payment_awarded_to_tutor INTEGER DEFAULT 0")

    if not column_exists(cur, "tutor_requests", "paid_at"):
        cur.execute("ALTER TABLE tutor_requests ADD COLUMN paid_at TEXT")

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
                user_id, language, manual_language, is_admin, is_tutor,
                phone, full_name, telegram_username, user_balance_stars, premium_until, pending_payment,
                premium_remind_3days_sent, premium_expired_sent
            )
            VALUES (?, 'ua', 0, 0, 0, NULL, NULL, NULL, 0, NULL, NULL, 0, 0)
        """, (user_id,))
        conn.commit()

    conn.close()


def get_user(user_id: int):
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, language, manual_language, is_admin, is_tutor,
               phone, full_name, telegram_username, user_balance_stars, premium_until, pending_payment,
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
        "is_tutor": bool(row[4]),
        "phone": row[5],
        "full_name": row[6],
        "telegram_username": row[7],
        "user_balance_stars": int(row[8] or 0),
        "premium_until": row[9],
        "pending_payment": row[10],
        "premium_remind_3days_sent": bool(row[11]),
        "premium_expired_sent": bool(row[12]),
    }


def detect_language_code(language_code: str):
    if not language_code:
        return "ua"
    code = language_code.lower()
    if code.startswith("ru"):
        return "ru"
    return "ua"


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


def set_user_phone(user_id: int, phone: str):
    ensure_user(user_id)
    normalized = normalize_phone(phone)
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET phone = ?
        WHERE user_id = ?
    """, (normalized, user_id))
    conn.commit()
    conn.close()


def set_user_full_name(user_id: int, full_name: str):
    ensure_user(user_id)
    value = (full_name or "").strip()
    if not value:
        return

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET full_name = ?
        WHERE user_id = ?
    """, (value, user_id))
    conn.commit()
    conn.close()


def sync_user_telegram_name(user: types.User | None):
    if not user:
        return
    full_name = get_telegram_full_name(user)
    if full_name:
        set_user_full_name(user.id, full_name)
    set_user_username(user.id, getattr(user, "username", None))


def resolve_user_language(message: types.Message):
    user_id = message.from_user.id
    ensure_user(user_id)
    sync_user_telegram_name(message.from_user)
    user = get_user(user_id)

    if user["manual_language"]:
        return user["language"] or "ua"

    detected = detect_language_code(message.from_user.language_code)
    set_user_language(user_id, detected, manual=False)
    return detected


async def ensure_contact_shared(message: types.Message, lang: str | None = None) -> bool:
    ensure_user(message.from_user.id)
    sync_user_telegram_name(message.from_user)
    user = get_user(message.from_user.id)
    if user.get("phone"):
        return True

    lang = lang or resolve_user_language(message)
    user_state[message.from_user.id] = "start_phone_wait"
    await message.answer(TEXTS[lang]["start_phone_request"], reply_markup=get_start_phone_menu(lang))
    return False


def build_balance_topup_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    for amount in TOP_UP_AMOUNT_OPTIONS:
        kb.insert(InlineKeyboardButton(f"{amount}⭐", callback_data=f"balance_topup:{amount}"))
    return kb


async def send_balance_topup_invoice(chat_id: int, amount: int, lang: str):
    await bot.send_invoice(
        chat_id=chat_id,
        title=TEXTS[lang]["balance_top_up_invoice_title"],
        description=TEXTS[lang]["balance_top_up_invoice_description"],
        payload=f"balance_topup_{amount}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"{TEXTS[lang]['balance_top_up_btn']} {amount}⭐", amount=amount)],
        start_parameter=f"balance_topup_{amount}"
    )


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


def logout_tutor(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_tutor = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_tutor_user(user_id: int):
    return get_user(user_id)["is_tutor"]


def get_tutor_profile(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, full_name, phone, created_at
        FROM tutor_profiles
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "full_name": row[2],
        "phone": row[3],
        "created_at": row[4],
    }

def get_tutor_profile_by_phone(phone: str):
    normalized = normalize_phone(phone)
    if not normalized:
        return None

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, full_name, phone, created_at
        FROM tutor_profiles
        WHERE phone = ?
    """, (normalized,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "full_name": row[2],
        "phone": row[3],
        "created_at": row[4],
    }


def get_display_name_for_user(user_id: int) -> str:
    user = get_user(user_id)
    if user.get("full_name"):
        return user["full_name"]
    return f"user_{user_id}"


def register_tutor_profile(user_id: int, full_name: str, phone: str):
    ensure_user(user_id)
    normalized = normalize_phone(phone)
    full_name = (full_name or "").strip() or get_display_name_for_user(user_id)

    conn = db()
    cur = conn.cursor()

    existing = get_tutor_profile_by_phone(normalized)
    if existing:
        cur.execute("""
            UPDATE tutor_profiles
            SET user_id = ?, full_name = ?
            WHERE id = ?
        """, (user_id, full_name, existing["id"]))
    else:
        cur.execute("""
            INSERT INTO tutor_profiles (user_id, full_name, phone, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, full_name, normalized, datetime.now(timezone.utc).isoformat()))

    cur.execute("UPDATE users SET is_tutor = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def login_tutor_by_phone(user_id: int, phone: str) -> bool:
    ensure_user(user_id)
    normalized = normalize_phone(phone)
    profile = get_tutor_profile_by_phone(normalized)

    if not profile:
        return False

    current_name = get_display_name_for_user(user_id)

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tutor_profiles
        SET user_id = ?, full_name = ?
        WHERE id = ?
    """, (user_id, current_name, profile["id"]))
    cur.execute("UPDATE users SET is_tutor = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


def ensure_tutor_balance(tutor_user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT tutor_user_id FROM tutor_balances WHERE tutor_user_id = ?", (tutor_user_id,))
    row = cur.fetchone()

    if not row:
        cur.execute(
            "INSERT INTO tutor_balances (tutor_user_id, balance_stars) VALUES (?, 0)",
            (tutor_user_id,)
        )
        conn.commit()

    conn.close()


def get_tutor_balance(tutor_user_id: int) -> int:
    ensure_tutor_balance(tutor_user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT balance_stars FROM tutor_balances WHERE tutor_user_id = ?", (tutor_user_id,))
    row = cur.fetchone()
    conn.close()
    return int(row[0]) if row else 0


def add_tutor_balance(tutor_user_id: int, amount_stars: int, request_id: int | None = None, note: str = ""):
    ensure_tutor_balance(tutor_user_id)
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tutor_balances
        SET balance_stars = balance_stars + ?
        WHERE tutor_user_id = ?
    """, (amount_stars, tutor_user_id))

    cur.execute("""
        INSERT INTO tutor_balance_history (
            tutor_user_id, request_id, amount_stars, note, created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        tutor_user_id,
        request_id,
        amount_stars,
        note,
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()


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


def get_payment_amount_for_type(payment_type: str) -> int:
    if payment_type == "task":
        return 250
    if payment_type == "complex":
        return 500
    return 0


def get_tutor_reward_for_payment_amount(amount_stars: int) -> int:
    return int(amount_stars * 0.5)


def save_tutor_request(
    user_id: int,
    category: str,
    subject: str,
    client_name: str,
    phone: str,
    level: str = "",
    goal: str = "",
    preferred_time: str = "",
    lesson_format: str = "",
    payment_type: str = "",
    payment_amount_stars: int = 0
):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tutor_requests (
            user_id, category, subject, client_name, phone,
            level, goal, preferred_time, lesson_format, status,
            admin_reply, created_at, assigned_tutor_id,
            payment_type, payment_amount_stars,
            payment_awarded_to_tutor, paid_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, NULL, ?, ?, 0, ?)
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
        datetime.now(timezone.utc).isoformat(),
        payment_type,
        payment_amount_stars,
        datetime.now(timezone.utc).isoformat() if payment_amount_stars > 0 else None
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


def get_unassigned_tutor_requests():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, category, subject, client_name, phone, level, goal,
               preferred_time, lesson_format, created_at, payment_type, payment_amount_stars
        FROM tutor_requests
        WHERE status = ?
          AND assigned_tutor_id IS NULL
          AND payment_amount_stars > 0
        ORDER BY id DESC
    """, (REQUEST_STATUS_NEW,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_tutor_assigned_requests(tutor_user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, category, subject, client_name, phone, level, goal,
               preferred_time, lesson_format, status, created_at
        FROM tutor_requests
        WHERE assigned_tutor_id = ?
        ORDER BY id DESC
    """, (tutor_user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_request_by_id(request_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, category, subject, client_name, phone, level, goal,
               preferred_time, lesson_format, status, created_at, assigned_tutor_id,
               payment_type, payment_amount_stars, payment_awarded_to_tutor, paid_at
        FROM tutor_requests
        WHERE id = ?
    """, (request_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "category": row[2],
        "subject": row[3],
        "client_name": row[4],
        "phone": row[5],
        "level": row[6],
        "goal": row[7],
        "preferred_time": row[8],
        "lesson_format": row[9],
        "status": row[10],
        "created_at": row[11],
        "assigned_tutor_id": row[12],
        "payment_type": row[13],
        "payment_amount_stars": row[14] or 0,
        "payment_awarded_to_tutor": bool(row[15]),
        "paid_at": row[16],
    }


def try_award_tutor_for_request(request_id: int):
    request_data = get_request_by_id(request_id)
    if not request_data:
        return

    if not request_data["assigned_tutor_id"]:
        return

    if request_data["payment_awarded_to_tutor"]:
        return

    if request_data["payment_amount_stars"] <= 0:
        return

    reward = get_tutor_reward_for_payment_amount(request_data["payment_amount_stars"])
    if reward <= 0:
        return

    add_tutor_balance(
        tutor_user_id=request_data["assigned_tutor_id"],
        amount_stars=reward,
        request_id=request_id,
        note=f"50% від оплати за заявку #{request_id}"
    )
    add_user_balance(
        user_id=request_data["assigned_tutor_id"],
        amount_stars=reward,
        note=f"Tutor reward for request #{request_id}"
    )

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tutor_requests
        SET payment_awarded_to_tutor = 1
        WHERE id = ?
    """, (request_id,))
    conn.commit()
    conn.close()


def assign_request_to_tutor(request_id: int, tutor_user_id: int) -> bool:
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT status, assigned_tutor_id, payment_amount_stars
        FROM tutor_requests
        WHERE id = ?
    """, (request_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    status, assigned_tutor_id, payment_amount_stars = row
    if assigned_tutor_id is not None or status != REQUEST_STATUS_NEW or (payment_amount_stars or 0) <= 0:
        conn.close()
        return False

    cur.execute("""
        UPDATE tutor_requests
        SET assigned_tutor_id = ?, status = ?
        WHERE id = ?
    """, (tutor_user_id, REQUEST_STATUS_ACCEPTED, request_id))
    conn.commit()
    conn.close()

    try_award_tutor_for_request(request_id)
    return True


def get_request_files(request_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, sender_user_id, sender_role, file_id, file_name, created_at
        FROM request_files
        WHERE request_id = ?
        ORDER BY id ASC
    """, (request_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def save_request_file(request_id: int, sender_user_id: int, sender_role: str, file_id: str, file_name: str | None):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO request_files (
            request_id, sender_user_id, sender_role, file_id, file_name, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request_id,
        sender_user_id,
        sender_role,
        file_id,
        file_name or "",
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()


def get_latest_active_assigned_request_for_user(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, assigned_tutor_id
        FROM tutor_requests
        WHERE user_id = ?
          AND assigned_tutor_id IS NOT NULL
          AND status IN (?, ?, ?)
        ORDER BY id DESC
        LIMIT 1
    """, (user_id, REQUEST_STATUS_ACCEPTED, REQUEST_STATUS_IN_PROGRESS, REQUEST_STATUS_NEW))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {"id": row[0], "assigned_tutor_id": row[1]}


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
    cur.execute("""
        SELECT user_id, language, is_admin, is_tutor, premium_until
        FROM users
        WHERE user_id = ?
    """, (user_id,))
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

    if is_admin_user(user_id):
        role = TEXTS[lang]["profile_admin"]
    elif is_tutor_user(user_id):
        role = TEXTS[lang]["profile_tutor"]
    else:
        role = TEXTS[lang]["profile_user"]

    status = get_profile_status_text(user_id, lang)
    language_name = LANG_NAMES.get(user["language"], user["language"])

    lines = [
        TEXTS[lang]["profile_title"],
        "",
        f"{TEXTS[lang]['profile_role']}: {role}",
        f"{TEXTS[lang]['profile_language']}: {language_name}",
        f"{TEXTS[lang]['profile_status']}: {status}",
        f"{TEXTS[lang]['balance_label']}: {get_user_balance(user_id)}⭐",
    ]

    if user.get("full_name"):
        lines.append(f"{TEXTS[lang]['tutor_name']}: {user['full_name']}")

    if user.get("telegram_username"):
        lines.append(f"{TEXTS[lang]['telegram_username_label']}: @{user['telegram_username']}")

    if user.get("phone"):
        lines.append(f"{TEXTS[lang]['tutor_phone']}: {user['phone']}")

    referrer_id = get_referrer_for_user(user_id)
    if referrer_id:
        lines.append(f"{TEXTS[lang]['referrer_label']}: {referrer_id}")

    tutor_profile = get_tutor_profile(user_id)
    if tutor_profile:
        lines.append(f"{TEXTS[lang]['tutor_balance_label']}: {get_tutor_balance(user_id)}⭐")

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


def build_tutor_panel_text(user_id: int, lang: str):
    tutor_profile = get_tutor_profile(user_id)
    user = get_user(user_id)
    display_name = tutor_profile["full_name"] if tutor_profile else (user.get("full_name") or f"user_{user_id}")
    balance = get_tutor_balance(user_id)

    if balance >= 1000:
        withdraw_status = TEXTS[lang]["tutor_panel_withdraw_status_ready"]
    else:
        withdraw_status = TEXTS[lang]["tutor_panel_withdraw_status_wait"].format(remaining=1000 - balance)

    lines = [
        TEXTS[lang]["tutor_panel_title"],
        "",
        f"{TEXTS[lang]['tutor_panel_name']}: {display_name}",
        f"{TEXTS[lang]['tutor_panel_balance']}: {balance}⭐",
        withdraw_status,
    ]
    return "\n".join(lines)


def build_request_detail_text(request_data: dict, lang: str):
    payment_part = "-"
    if request_data.get("payment_amount_stars", 0) > 0:
        payment_part = f"{request_data.get('payment_type') or '-'} | {request_data.get('payment_amount_stars')}⭐"

    return (
        f"{TEXTS[lang]['tutor_request_detail_title']} #{request_data['id']}\n\n"
        f"{TEXTS[lang]['complaint_user_id']}: {request_data['user_id']}\n"
        f"{TEXTS[lang]['category_label']}: {request_data.get('category') or '-'}\n"
        f"{TEXTS[lang]['tutor_subject']}: {request_data.get('subject') or '-'}\n"
        f"{TEXTS[lang]['tutor_name']}: {request_data.get('client_name') or '-'}\n"
        f"{TEXTS[lang]['tutor_phone']}: {request_data.get('phone') or '-'}\n"
        f"{TEXTS[lang]['level_label']}: {request_data.get('level') or '-'}\n"
        f"{TEXTS[lang]['goal_label']}: {request_data.get('goal') or '-'}\n"
        f"{TEXTS[lang]['preferred_time_label']}: {request_data.get('preferred_time') or '-'}\n"
        f"{TEXTS[lang]['format_label']}: {request_data.get('lesson_format') or '-'}\n"
        f"Payment: {payment_part}\n"
        f"{TEXTS[lang]['status_label']}: {get_request_status_text(request_data.get('status', ''), lang)}"
    )


def main_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["task"])
    kb.row(TEXTS[lang]["tutor"])
    kb.row(TEXTS[lang]["support_btn"])
    kb.row(TEXTS[lang]["menu_btn"])
    return kb


def back_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["back"])
    return kb


def get_start_phone_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(TEXTS[lang].get("share_phone_btn", "📱 Поділитися номером"), request_contact=True))
    return kb


def system_menu(lang: str = "ua", is_admin: bool = False, is_tutor: bool = False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["my_profile_btn"])
    kb.row(TEXTS[lang]["balance_top_up_btn"], TEXTS[lang]["referral_link_btn"])

    if is_tutor:
        kb.row(TEXTS[lang]["tutor_profile_btn"])
        kb.row(TEXTS[lang]["tutor_logout_btn"])
    else:
        kb.row(TEXTS[lang]["tutor_login_btn"])

    if is_admin:
        kb.row(TEXTS[lang]["admin_profile_btn"])
        kb.row(TEXTS[lang]["admin_balance_btn"])
        kb.row(TEXTS[lang]["admin_logout_btn"])
    else:
        kb.row(TEXTS[lang]["admin_login_btn"])

    kb.row(TEXTS[lang]["premium_menu_btn"])
    kb.row(TEXTS[lang]["change_language_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def premium_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["back"])
    return kb


def profile_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["balance_top_up_btn"], TEXTS[lang]["referral_link_btn"])
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
    kb.row(TEXTS[lang]["admin_balance_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def tutor_menu(user_id: int, lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["tutor_new_requests_btn"])
    kb.row(TEXTS[lang]["tutor_my_requests_btn"])
    kb.row(get_tutor_withdraw_button_text(user_id, lang))
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


def get_request_confirm_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["confirm_btn"], TEXTS[lang]["edit_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb

def build_take_request_keyboard(request_id: int, lang: str):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        TEXTS[lang]["tutor_take_request_btn"],
        callback_data=f"take_request:{request_id}"
    ))
    return kb


def build_tutor_requests_keyboard(rows, lang: str):
    kb = InlineKeyboardMarkup()
    for row in rows:
        request_id = row[0]
        subject = row[3]
        kb.add(InlineKeyboardButton(
            f"#{request_id} | {subject}",
            callback_data=f"open_tutor_request:{request_id}"
        ))
    return kb


def build_tutor_request_actions_keyboard(request_id: int, lang: str):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        TEXTS[lang]["tutor_write_user_btn"],
        callback_data=f"tutor_msg_user:{request_id}"
    ))
    kb.add(InlineKeyboardButton(
        TEXTS[lang]["tutor_send_file_btn"],
        callback_data=f"tutor_file_user:{request_id}"
    ))
    return kb


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("balance_topup:"))
async def balance_topup_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user(user_id)["language"] or "ua"
    try:
        amount = int(callback_query.data.split(":", 1)[1])
    except Exception:
        await callback_query.answer(TEXTS[lang]["error_try_again"], show_alert=True)
        return

    await send_balance_topup_invoice(callback_query.message.chat.id, amount, lang)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("take_request:"))
async def take_request_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user(user_id)["language"] or "ua"
    sync_user_telegram_name(callback_query.from_user)

    if not is_tutor_user(user_id):
        await callback_query.answer(TEXTS[lang]["no_access"], show_alert=True)
        return

    request_id = int(callback_query.data.split(":")[1])

    if not assign_request_to_tutor(request_id, user_id):
        await callback_query.answer(TEXTS[lang]["tutor_take_failed"], show_alert=True)
        return

    request_data = get_request_by_id(request_id)
    if request_data:
        try:
            await bot.send_message(request_data["user_id"], TEXTS[lang]["tutor_request_taken_user"])
        except Exception as e:
            logging.warning(f"Failed to notify user about tutor assignment: {e}")

    await callback_query.answer(TEXTS[lang]["tutor_take_success"])
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer(
        f"{TEXTS[lang]['tutor_take_success']}\n\n{build_tutor_panel_text(user_id, lang)}",
        reply_markup=tutor_menu(user_id, lang)
    )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("open_tutor_request:"))
async def open_tutor_request_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user(user_id)["language"] or "ua"
    sync_user_telegram_name(callback_query.from_user)

    if not is_tutor_user(user_id):
        await callback_query.answer(TEXTS[lang]["no_access"], show_alert=True)
        return

    request_id = int(callback_query.data.split(":")[1])
    request_data = get_request_by_id(request_id)

    if not request_data or request_data["assigned_tutor_id"] != user_id:
        await callback_query.answer(TEXTS[lang]["no_access"], show_alert=True)
        return

    lines = [build_request_detail_text(request_data, lang), ""]
    files = get_request_files(request_id)
    lines.append(TEXTS[lang]["request_files_title"] + ":")

    if files:
        for _, _, sender_role, _, file_name, created_at in files:
            sender_text = "user" if sender_role == "user" else "tutor"
            lines.append(f"• {file_name or 'file'} | {sender_text} | {created_at[:16]}")
    else:
        lines.append(TEXTS[lang]["no_request_files"])

    user_state[user_id] = "tutor_panel"
    await callback_query.message.answer(
        "\n".join(lines),
        reply_markup=build_tutor_request_actions_keyboard(request_id, lang)
    )
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("tutor_msg_user:"))
async def tutor_msg_user_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user(user_id)["language"] or "ua"
    sync_user_telegram_name(callback_query.from_user)

    if not is_tutor_user(user_id):
        await callback_query.answer(TEXTS[lang]["no_access"], show_alert=True)
        return

    request_id = int(callback_query.data.split(":")[1])
    request_data = get_request_by_id(request_id)

    if not request_data or request_data["assigned_tutor_id"] != user_id:
        await callback_query.answer(TEXTS[lang]["no_access"], show_alert=True)
        return

    user_temp.setdefault(user_id, {})
    user_temp[user_id]["reply_user_id"] = request_data["user_id"]
    user_temp[user_id]["reply_request_id"] = request_id
    user_state[user_id] = "tutor_reply_text_wait"

    await callback_query.message.answer(TEXTS[lang]["tutor_reply_text_prompt"], reply_markup=back_menu(lang))
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("tutor_file_user:"))
async def tutor_file_user_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user(user_id)["language"] or "ua"
    sync_user_telegram_name(callback_query.from_user)

    if not is_tutor_user(user_id):
        await callback_query.answer(TEXTS[lang]["no_access"], show_alert=True)
        return

    request_id = int(callback_query.data.split(":")[1])
    request_data = get_request_by_id(request_id)

    if not request_data or request_data["assigned_tutor_id"] != user_id:
        await callback_query.answer(TEXTS[lang]["no_access"], show_alert=True)
        return

    user_temp.setdefault(user_id, {})
    user_temp[user_id]["reply_user_id"] = request_data["user_id"]
    user_temp[user_id]["reply_request_id"] = request_id
    user_state[user_id] = "tutor_send_file_wait"

    await callback_query.message.answer(TEXTS[lang]["tutor_send_file_prompt"], reply_markup=back_menu(lang))
    await callback_query.answer()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    is_new_user = not user_exists(message.from_user.id)
    ensure_user(message.from_user.id)
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)

    referrer_id = get_start_referrer_id(message)
    if is_new_user and referrer_id and award_referral_bonus(referrer_id, message.from_user.id):
        try:
            ref_lang = get_user(referrer_id)["language"] or "ua"
            await bot.send_message(referrer_id, TEXTS[ref_lang]["referral_reward_received"])
        except Exception as e:
            logging.warning(f"Failed to notify referrer {referrer_id}: {e}")

    user_state[message.from_user.id] = "start_phone_wait"
    await message.answer(TEXTS[lang]["start_phone_request"], reply_markup=get_start_phone_menu(lang))


@dp.message_handler(commands=["myprofile"])
async def cmd_myprofile(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    if not await ensure_contact_shared(message, lang):
        return
    user_state[message.from_user.id] = "system_menu"
    await message.answer(
        build_profile_text(message.from_user.id, lang),
        reply_markup=system_menu(
            lang,
            is_admin=is_admin_user(message.from_user.id),
            is_tutor=is_tutor_user(message.from_user.id)
        )
    )


@dp.message_handler(commands=["premium"])
async def cmd_premium(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    if not await ensure_contact_shared(message, lang):
        return
    user_state[message.from_user.id] = "premium_profile_screen"
    await message.answer(TEXTS[lang]["premium_profile_info"], reply_markup=premium_menu(lang))
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


@dp.message_handler(commands=["complaint"])
async def cmd_complaint(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    if not await ensure_contact_shared(message, lang):
        return
    user_state[message.from_user.id] = "complaint_wait"
    await message.answer(TEXTS[lang]["support_text"], reply_markup=back_menu(lang))


@dp.message_handler(commands=["language"])
async def cmd_language(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    if not await ensure_contact_shared(message, lang):
        return
    user_state[message.from_user.id] = "language_menu"
    await message.answer(TEXTS[lang]["language_text"], reply_markup=get_language_keyboard(lang))


@dp.message_handler(commands=["admin"])
async def cmd_admin(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    if not await ensure_contact_shared(message, lang):
        return
    user_state[message.from_user.id] = "admin_login_wait"
    await message.answer(TEXTS[lang]["ask_admin_login"], reply_markup=back_menu(lang))

@dp.message_handler(lambda m: m.text in LANG_BUTTONS)
async def set_language(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = LANG_BUTTONS[message.text]
    set_user_language(message.from_user.id, lang, manual=True)
    user_state[message.from_user.id] = "main"
    await message.answer(TEXTS[lang]["main_menu_hint"], reply_markup=main_menu(lang))


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    payload = message.successful_payment.invoice_payload

    if payload.startswith("balance_topup_"):
        amount = int(payload.split("_")[-1])
        add_user_balance(message.from_user.id, amount, note="Telegram Stars top up")
        add_payment(message.from_user.id, "balance_top_up", amount)
        await message.answer(
            TEXTS[lang]["balance_top_up_success"].format(amount=amount),
            reply_markup=system_menu(
                lang,
                is_admin=is_admin_user(message.from_user.id),
                is_tutor=is_tutor_user(message.from_user.id)
            )
        )
        return

    if payload == "task_payment":
        set_pending_payment(message.from_user.id, "task")
        add_payment(message.from_user.id, "Одне завдання", 250)
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_task']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=back_menu(lang)
        )
        return

    if payload == "complex_payment":
        set_pending_payment(message.from_user.id, "complex")
        add_payment(message.from_user.id, "Комплексне виконання роботи", 500)
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_complex']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=back_menu(lang)
        )
        return

    if payload == "premium_profile_payment":
        activate_premium(message.from_user.id, days=30)
        add_payment(message.from_user.id, "Преміум профіль", 2500)
        user_state[message.from_user.id] = "main"
        await message.answer(
            f"{TEXTS[lang]['pay_success_premium_profile']}\n\n{TEXTS[lang]['premium_profile_activated']}",
            reply_markup=main_menu(lang)
        )
        return


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    if not await ensure_contact_shared(message, lang):
        return
    state = user_state.get(message.from_user.id, "main")
    pending_payment = get_pending_payment(message.from_user.id)

    if state == "tutor_send_file_wait":
        if not is_tutor_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        reply_user_id = user_temp.get(message.from_user.id, {}).get("reply_user_id")
        request_id = user_temp.get(message.from_user.id, {}).get("reply_request_id")

        if not reply_user_id or not request_id:
            user_state[message.from_user.id] = "tutor_panel"
            await message.answer(TEXTS[lang]["error_try_again"], reply_markup=tutor_menu(message.from_user.id, lang))
            return

        caption = f"{TEXTS[lang]['file_from_tutor_caption']} #{request_id}"
        try:
            await bot.send_document(
                chat_id=reply_user_id,
                document=message.document.file_id,
                caption=caption
            )
            save_request_file(
                request_id=request_id,
                sender_user_id=message.from_user.id,
                sender_role="tutor",
                file_id=message.document.file_id,
                file_name=message.document.file_name
            )
            await message.answer(
                f"{TEXTS[lang]['tutor_send_file_sent']}\n\n{build_tutor_panel_text(message.from_user.id, lang)}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
        except Exception as e:
            await message.answer(f"❌ {e}", reply_markup=tutor_menu(message.from_user.id, lang))

        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "tutor_panel"
        return

    if pending_payment in {"task", "complex"}:
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
        user_state[message.from_user.id] = "main"
        return

    active_request = get_latest_active_assigned_request_for_user(message.from_user.id)
    if active_request:
        request_id = active_request["id"]
        tutor_user_id = active_request["assigned_tutor_id"]

        save_request_file(
            request_id=request_id,
            sender_user_id=message.from_user.id,
            sender_role="user",
            file_id=message.document.file_id,
            file_name=message.document.file_name
        )

        try:
            await bot.send_document(
                chat_id=tutor_user_id,
                document=message.document.file_id,
                caption=f"{TEXTS[lang]['file_from_user_caption']} #{request_id}"
            )
        except Exception as e:
            logging.warning(f"Failed to send request file to tutor {tutor_user_id}: {e}")

        await message.answer(TEXTS[lang]["file_sent_to_tutor"], reply_markup=main_menu(lang))
        return

    await message.answer(TEXTS[lang]["no_payment"], reply_markup=main_menu(lang))


@dp.message_handler(content_types=types.ContentType.TEXT)
async def menu(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    if user_state.get(message.from_user.id) != "start_phone_wait" and not await ensure_contact_shared(message, lang):
        return
    state = user_state.get(message.from_user.id, "main")
    text = message.text

    if state == "start_phone_wait":
        await message.answer(TEXTS[lang]["start_phone_request"], reply_markup=get_start_phone_menu(lang))
        return

    # ---------------------------
    # ГЛОБАЛЬНА НАВІГАЦІЯ
    # ---------------------------

    if text == TEXTS[lang]["back"]:
        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["main_menu_hint"], reply_markup=main_menu(lang))
        return

    if text == TEXTS[lang]["menu_btn"]:
        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "system_menu"
        await message.answer(
            TEXTS[lang]["system_menu_title"],
            reply_markup=system_menu(
                lang,
                is_admin=is_admin_user(message.from_user.id),
                is_tutor=is_tutor_user(message.from_user.id)
            )
        )
        return

    if text == TEXTS[lang]["my_profile_btn"]:
        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "system_menu"
        await message.answer(
            TEXTS[lang]["system_menu_title"],
            reply_markup=system_menu(
                lang,
                is_admin=is_admin_user(message.from_user.id),
                is_tutor=is_tutor_user(message.from_user.id)
            )
        )
        return

    if text == TEXTS[lang]["balance_top_up_btn"]:
        user_state[message.from_user.id] = "system_menu"
        await message.answer(TEXTS[lang]["balance_top_up_title"], reply_markup=build_balance_topup_keyboard())
        return

    if text == TEXTS[lang]["referral_link_btn"]:
        referral_link = get_bot_referral_link(message.from_user.id)
        if not referral_link:
            await message.answer(TEXTS[lang]["referral_link_unavailable"], reply_markup=system_menu(
                lang,
                is_admin=is_admin_user(message.from_user.id),
                is_tutor=is_tutor_user(message.from_user.id)
            ))
            return
        await message.answer(f"{referral_link}\n\n{TEXTS[lang]['referral_link_text']}", reply_markup=system_menu(
            lang,
            is_admin=is_admin_user(message.from_user.id),
            is_tutor=is_tutor_user(message.from_user.id)
        ))
        return

    if text == TEXTS[lang]["support_btn"]:
        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "complaint_wait"
        await message.answer(TEXTS[lang]["support_text"], reply_markup=back_menu(lang))
        return

    if text == TEXTS[lang]["task"]:
        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "task_menu"
        await message.answer(TEXTS[lang]["choose_service"], reply_markup=get_task_menu(lang))
        return

    if text == TEXTS[lang]["tutor"]:
        user_temp[message.from_user.id] = {}
        user_state[message.from_user.id] = "tutor_category_wait"
        await message.answer(TEXTS[lang]["categories_title"], reply_markup=get_tutor_categories_menu(lang))
        return

    # ---------------------------
    # STATE-ЛОГІКА
    # ---------------------------

    if state == "admin_login_wait":
        user_temp[message.from_user.id] = {"admin_login": text.strip()}
        user_state[message.from_user.id] = "admin_password_wait"
        await message.answer(TEXTS[lang]["ask_admin_password"], reply_markup=back_menu(lang))
        return

    if state == "admin_password_wait":
        login_value = user_temp.get(message.from_user.id, {}).get("admin_login", "")
        password_value = text.strip()

        if login_value == ADMIN_LOGIN and password_value == ADMIN_PASSWORD:
            add_admin(message.from_user.id)
            user_state[message.from_user.id] = "admin_panel"
            await message.answer(TEXTS[lang]["admin_login_success"], reply_markup=admin_menu(lang))
        else:
            user_temp.pop(message.from_user.id, None)
            user_state[message.from_user.id] = "main"
            await message.answer(TEXTS[lang]["admin_login_fail"], reply_markup=main_menu(lang))
        return

    if state == "tutor_reply_text_wait":
        if not is_tutor_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        reply_user_id = user_temp.get(message.from_user.id, {}).get("reply_user_id")
        if not reply_user_id:
            user_state[message.from_user.id] = "tutor_panel"
            await message.answer(TEXTS[lang]["error_try_again"], reply_markup=tutor_menu(message.from_user.id, lang))
            return

        try:
            await bot.send_message(reply_user_id, f"💬 Tutor:\n\n{text}")
            await message.answer(
                f"{TEXTS[lang]['tutor_reply_text_sent']}\n\n{build_tutor_panel_text(message.from_user.id, lang)}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
        except Exception as e:
            await message.answer(f"❌ {e}", reply_markup=tutor_menu(message.from_user.id, lang))

        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "tutor_panel"
        return

    if state == "tutor_withdraw_card_wait":
        if not is_tutor_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        card_number = text.strip()
        tutor_profile = get_tutor_profile(message.from_user.id)
        balance = get_tutor_balance(message.from_user.id)

        lines = [
            TEXTS[lang]["tutor_withdraw_request_title"],
            f"{TEXTS[lang]['complaint_user_id']}: {message.from_user.id}",
            f"{TEXTS[lang]['tutor_name']}: {tutor_profile['full_name'] if tutor_profile else get_display_name_for_user(message.from_user.id)}",
            f"{TEXTS[lang]['tutor_phone']}: {tutor_profile['phone'] if tutor_profile else '-'}",
            f"{TEXTS[lang]['card_number_label']}: {card_number}",
            f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐",
        ]

        if message.from_user.username:
            lines.append(f"{TEXTS[lang]['complaint_username']}: @{message.from_user.username}")

        admin_text = "\n".join(lines)

        for admin_id in get_admins():
            try:
                await bot.send_message(admin_id, admin_text)
            except Exception as e:
                logging.warning(f"Failed to send tutor withdraw request to admin {admin_id}: {e}")

        user_state[message.from_user.id] = "tutor_panel"
        await message.answer(
            f"{TEXTS[lang]['tutor_withdraw_sent']}\n\n{build_tutor_panel_text(message.from_user.id, lang)}",
            reply_markup=tutor_menu(message.from_user.id, lang)
        )
        return

    if state == "complaint_wait":
        user = get_user(message.from_user.id)
        if is_admin_user(message.from_user.id):
            profile_status = TEXTS[lang]["profile_admin"]
        elif is_tutor_user(message.from_user.id):
            profile_status = TEXTS[lang]["profile_tutor"]
        else:
            profile_status = get_profile_status_text(message.from_user.id, lang)

        language_name = LANG_NAMES.get(user["language"], user["language"])

        lines = [
            TEXTS[lang]["complaint_header"],
            f"{TEXTS[lang]['complaint_user_id']}: {message.from_user.id}",
            f"{TEXTS[lang]['complaint_language']}: {language_name}",
            f"{TEXTS[lang]['complaint_profile']}: {profile_status}",
            f"{TEXTS[lang]['tutor_phone']}: {user.get('phone') or '-'}",
        ]

        if user.get("full_name"):
            lines.append(f"{TEXTS[lang]['tutor_name']}: {user['full_name']}")

        if message.from_user.username:
            lines.append(f"{TEXTS[lang]['complaint_username']}: @{message.from_user.username}")

        premium_until = premium_until_text(message.from_user.id)
        if premium_until:
            lines.append(f"{TEXTS[lang]['profile_until']}: {premium_until}")

        lines.append("")
        lines.append(f"{TEXTS[lang]['complaint_text_label']}:")
        lines.append(text)

        complaint_text = "\n".join(lines)

        for admin_id in get_admins():
            try:
                await bot.send_message(admin_id, complaint_text)
            except Exception as e:
                logging.warning(f"Failed to send complaint to admin {admin_id}: {e}")

        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["complaint_sent"], reply_markup=main_menu(lang))
        return

    if state == "tutor_category_wait":
        if text not in SUBJECT_CATEGORIES:
            await message.answer(TEXTS[lang]["categories_title"], reply_markup=get_tutor_categories_menu(lang))
            return

        user_temp[message.from_user.id] = {"category": text}
        user_state[message.from_user.id] = "tutor_subject_wait"
        await message.answer(
            TEXTS[lang]["tutor_subject_title"],
            reply_markup=get_tutor_subjects_menu(text, lang)
        )
        return

    if state == "tutor_subject_wait":
        selected_category = user_temp.get(message.from_user.id, {}).get("category")
        valid_subjects = SUBJECT_CATEGORIES.get(selected_category, [])

        if text not in valid_subjects:
            await message.answer(
                TEXTS[lang]["choose_valid_subject"],
                reply_markup=get_tutor_subjects_menu(selected_category, lang)
            )
            return

        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["subject"] = text
        user_state[message.from_user.id] = "tutor_level_wait"
        await message.answer(TEXTS[lang]["ask_level"], reply_markup=back_menu(lang))
        return

    if state == "tutor_level_wait":
        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["level"] = text.strip()
        user_state[message.from_user.id] = "tutor_goal_wait"
        await message.answer(TEXTS[lang]["ask_goal"], reply_markup=back_menu(lang))
        return

    if state == "tutor_goal_wait":
        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["goal"] = text.strip()
        user_state[message.from_user.id] = "tutor_time_wait"
        await message.answer(TEXTS[lang]["ask_time"], reply_markup=back_menu(lang))
        return

    if state == "tutor_time_wait":
        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["preferred_time"] = text.strip()
        user_state[message.from_user.id] = "tutor_format_wait"
        await message.answer(TEXTS[lang]["ask_format"], reply_markup=back_menu(lang))
        return

    if state == "tutor_format_wait":
        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["lesson_format"] = text.strip()
        user_state[message.from_user.id] = "tutor_confirm_wait"

        d = user_temp[message.from_user.id]
        user_profile = get_user(message.from_user.id)
        client_name = user_profile.get("full_name") or get_display_name_for_user(message.from_user.id)

        confirm_text = (
            f"{TEXTS[lang]['request_confirm_text']}\n\n"
            f"{TEXTS[lang]['category_label']}: {d.get('category', '-')}\n"
            f"{TEXTS[lang]['tutor_subject']}: {d.get('subject', '-')}\n"
            f"{TEXTS[lang]['tutor_name']}: {client_name}\n"
            f"{TEXTS[lang]['tutor_phone']}: {user_profile.get('phone') or '-'}\n"
            f"{TEXTS[lang]['level_label']}: {d.get('level', '-')}\n"
            f"{TEXTS[lang]['goal_label']}: {d.get('goal', '-')}\n"
            f"{TEXTS[lang]['preferred_time_label']}: {d.get('preferred_time', '-')}\n"
            f"{TEXTS[lang]['format_label']}: {d.get('lesson_format', '-')}"
        )

        await message.answer(confirm_text, reply_markup=get_request_confirm_menu(lang))
        return

    if state == "tutor_confirm_wait":
        if text == TEXTS[lang]["edit_btn"]:
            user_state[message.from_user.id] = "tutor_category_wait"
            user_temp[message.from_user.id] = {}
            await message.answer(TEXTS[lang]["categories_title"], reply_markup=get_tutor_categories_menu(lang))
            return

        if text != TEXTS[lang]["confirm_btn"]:
            await message.answer(TEXTS[lang]["request_confirm_text"], reply_markup=get_request_confirm_menu(lang))
            return

        d = user_temp.get(message.from_user.id, {})
        user_profile = get_user(message.from_user.id)
        client_name = user_profile.get("full_name") or get_display_name_for_user(message.from_user.id)

        request_id = save_tutor_request(
            user_id=message.from_user.id,
            category=d.get("category", ""),
            subject=d.get("subject", ""),
            client_name=client_name,
            phone=user_profile.get("phone", ""),
            level=d.get("level", ""),
            goal=d.get("goal", ""),
            preferred_time=d.get("preferred_time", ""),
            lesson_format=d.get("lesson_format", ""),
            payment_type="",
            payment_amount_stars=0
        )

        language_name = LANG_NAMES.get(user_profile["language"], user_profile["language"])
        profile_status = get_profile_status_text(message.from_user.id, lang)

        admin_lines = [
            f"{TEXTS[lang]['tutor_request_header']} #{request_id}",
            f"{TEXTS[lang]['complaint_user_id']}: {message.from_user.id}",
            f"{TEXTS[lang]['complaint_language']}: {language_name}",
            f"{TEXTS[lang]['complaint_profile']}: {profile_status}",
            f"{TEXTS[lang]['tutor_name']}: {client_name}",
            f"{TEXTS[lang]['category_label']}: {d.get('category', '-')}",
            f"{TEXTS[lang]['tutor_subject']}: {d.get('subject', '-')}",
            f"{TEXTS[lang]['tutor_phone']}: {user_profile.get('phone') or '-'}",
            f"{TEXTS[lang]['level_label']}: {d.get('level', '-')}",
            f"{TEXTS[lang]['goal_label']}: {d.get('goal', '-')}",
            f"{TEXTS[lang]['preferred_time_label']}: {d.get('preferred_time', '-')}",
            f"{TEXTS[lang]['format_label']}: {d.get('lesson_format', '-')}",
            f"{TEXTS[lang]['status_label']}: {TEXTS[lang]['request_status_new']}",
        ]

        if message.from_user.username:
            admin_lines.append(f"{TEXTS[lang]['complaint_username']}: @{message.from_user.username}")

        premium_until = premium_until_text(message.from_user.id)
        if premium_until:
            admin_lines.append(f"{TEXTS[lang]['profile_until']}: {premium_until}")

        admin_text = "\n".join(admin_lines)

        for admin_id in get_admins():
            try:
                await bot.send_message(admin_id, admin_text)
            except Exception as e:
                logging.warning(f"Failed to send tutor request to admin {admin_id}: {e}")

        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["tutor_request_sent"], reply_markup=main_menu(lang))
        return

    if state == "admin_balance_lookup_wait":
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        target_user_id = find_user_id_by_identifier(text)
        if not target_user_id:
            await message.answer(TEXTS[lang]["admin_balance_user_not_found"], reply_markup=admin_menu(lang))
            user_state[message.from_user.id] = "admin_panel"
            return

        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["balance_target_user_id"] = target_user_id
        target_user = get_user(target_user_id)
        username_value = target_user.get("telegram_username")
        username_line = f"@{username_value}" if username_value else "-"
        user_state[message.from_user.id] = "admin_balance_amount_wait"
        await message.answer(
            f"{TEXTS[lang]['admin_balance_user_found']}: {target_user_id}\n"
            f"{TEXTS[lang]['admin_balance_current']}: {get_user_balance(target_user_id)}⭐\n"
            f"{TEXTS[lang]['tutor_name']}: {target_user.get('full_name') or '-'}\n"
            f"{TEXTS[lang]['tutor_phone']}: {target_user.get('phone') or '-'}\n"
            f"{TEXTS[lang]['telegram_username_label']}: {username_line}\n\n"
            f"{TEXTS[lang]['admin_balance_amount_prompt']}",
            reply_markup=back_menu(lang)
        )
        return

    if state == "admin_balance_amount_wait":
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        target_user_id = user_temp.get(message.from_user.id, {}).get("balance_target_user_id")
        operation = parse_balance_change_input(text)
        if not target_user_id or not operation:
            await message.answer(TEXTS[lang]["admin_balance_invalid_amount"], reply_markup=back_menu(lang))
            return

        mode, amount_value = operation
        old_balance = get_user_balance(target_user_id)
        if mode == "set":
            new_balance = set_user_balance(target_user_id, amount_value)
        else:
            new_balance = add_user_balance(target_user_id, amount_value, note="Admin balance change")
        diff = new_balance - old_balance

        target_lang = get_user(target_user_id)["language"] or lang
        try:
            await bot.send_message(
                target_user_id,
                TEXTS[target_lang]["admin_balance_notification"].format(amount=diff, balance=new_balance)
            )
        except Exception as e:
            logging.warning(f"Failed to notify user about balance change: {e}")

        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "admin_panel"
        await message.answer(
            f"{TEXTS[lang]['admin_balance_changed']}\n"
            f"ID: {target_user_id}\n"
            f"{TEXTS[lang]['admin_balance_current']}: {new_balance}⭐",
            reply_markup=admin_menu(lang)
        )
        return

    if state == "admin_search_wait":
        if not text.isdigit():
            await message.answer(TEXTS[lang]["admin_search_prompt"], reply_markup=back_menu(lang))
            return

        target_user_id = int(text)
        user_row, requests, payments = search_user_by_id(target_user_id)

        if not user_row:
            await message.answer(TEXTS[lang]["user_not_found"], reply_markup=admin_menu(lang))
            user_state[message.from_user.id] = "admin_panel"
            return

        _, user_language, is_admin_flag, is_tutor_flag, premium_until = user_row

        if is_admin_flag:
            role = TEXTS[lang]["profile_admin"]
        elif is_tutor_flag:
            role = TEXTS[lang]["profile_tutor"]
        else:
            role = TEXTS[lang]["profile_user"]

        status = TEXTS[lang]["profile_premium"] if premium_until else TEXTS[lang]["profile_basic"]

        lines = [
            f"{TEXTS[lang]['user_search_title']} {target_user_id}",
            f"{TEXTS[lang]['profile_role']}: {role}",
            f"{TEXTS[lang]['profile_language']}: {LANG_NAMES.get(user_language, user_language)}",
            f"{TEXTS[lang]['profile_status']}: {status}",
        ]

        target_user = get_user(target_user_id)
        lines.append(f"{TEXTS[lang]['balance_label']}: {get_user_balance(target_user_id)}⭐")
        if target_user.get("full_name"):
            lines.append(f"{TEXTS[lang]['tutor_name']}: {target_user['full_name']}")

        if target_user.get("telegram_username"):
            lines.append(f"{TEXTS[lang]['telegram_username_label']}: @{target_user['telegram_username']}")

        if target_user.get("phone"):
            lines.append(f"{TEXTS[lang]['tutor_phone']}: {target_user['phone']}")

        if premium_until:
            lines.append(f"{TEXTS[lang]['profile_until']}: {premium_until[:16]}")

        lines.append("")
        lines.append(TEXTS[lang]["orders_history_title"] + ":")

        if requests:
            for subject, status_code, created_at in requests:
                lines.append(f"• {subject} | {get_request_status_text(status_code, lang)} | {created_at[:16]}")
        else:
            lines.append(TEXTS[lang]["no_requests"])

        lines.append("")
        lines.append(TEXTS[lang]["payments_history_title"] + ":")

        if payments:
            for payment_type, amount_stars, created_at in payments:
                lines.append(f"• {payment_type} | {amount_stars}⭐ | {created_at[:16]}")
        else:
            lines.append(TEXTS[lang]["no_payments_history"])

        await message.answer("\n".join(lines), reply_markup=admin_menu(lang))
        user_state[message.from_user.id] = "admin_panel"
        return

    if state == "admin_reply_user_wait":
        if not text.isdigit():
            await message.answer(TEXTS[lang]["admin_reply_prompt"], reply_markup=back_menu(lang))
            return

        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["reply_user_id"] = int(text)
        user_state[message.from_user.id] = "admin_reply_text_wait"
        await message.answer(TEXTS[lang]["admin_reply_text_prompt"], reply_markup=back_menu(lang))
        return

    if state == "admin_reply_text_wait":
        reply_user_id = user_temp.get(message.from_user.id, {}).get("reply_user_id")
        if not reply_user_id:
            user_state[message.from_user.id] = "admin_panel"
            await message.answer(TEXTS[lang]["error_try_again"], reply_markup=admin_menu(lang))
            return

        try:
            await bot.send_message(reply_user_id, f"{TEXTS[lang]['admin_message_prefix']}{text}")
            await message.answer(TEXTS[lang]["admin_reply_sent"], reply_markup=admin_menu(lang))
        except Exception as e:
            await message.answer(f"❌ Не вдалося відправити повідомлення: {e}", reply_markup=admin_menu(lang))

        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "admin_panel"
        return

    if text == TEXTS[lang]["admin_login_btn"]:
        user_state[message.from_user.id] = "admin_login_wait"
        await message.answer(TEXTS[lang]["ask_admin_login"], reply_markup=back_menu(lang))
        return

    if text == TEXTS[lang]["admin_profile_btn"]:
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        user_state[message.from_user.id] = "admin_panel"
        await message.answer(TEXTS[lang]["admin_panel_title"], reply_markup=admin_menu(lang))
        return

    if text == TEXTS[lang]["admin_logout_btn"]:
        remove_admin(message.from_user.id)
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["admin_logout_success"], reply_markup=main_menu(lang))
        return

    if text == TEXTS[lang]["change_language_btn"]:
        user_state[message.from_user.id] = "language_menu"
        await message.answer(TEXTS[lang]["language_text"], reply_markup=get_language_keyboard(lang))
        return

    if text == TEXTS[lang]["premium_menu_btn"]:
        user_state[message.from_user.id] = "system_menu"
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

    if text == TEXTS[lang]["profile_upgrade_btn"]:
        user_state[message.from_user.id] = "premium_profile_screen"
        await message.answer(TEXTS[lang]["premium_profile_info"], reply_markup=premium_menu(lang))
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

    if text == TEXTS[lang]["one"]:
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Task Payment",
            description="Single task",
            payload="task_payment",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Task", amount=250)],
            start_parameter="task"
        )
        return

    if text == TEXTS[lang]["complex"]:
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Complex Payment",
            description="Complex work",
            payload="complex_payment",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Complex", amount=500)],
            start_parameter="complex"
        )
        return

    if text == TEXTS[lang]["premium_profile"]:
        user_state[message.from_user.id] = "task_menu"
        await message.answer(
            TEXTS[lang]["premium_profile_info"],
            reply_markup=get_task_menu(lang)
        )
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

    if text == TEXTS[lang]["admin_new_requests_btn"]:
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        rows = get_new_requests()
        if not rows:
            await message.answer(TEXTS[lang]["admin_no_new_requests"], reply_markup=admin_menu(lang))
            return

        lines = [TEXTS[lang]["admin_new_requests_btn"] + ":"]
        for request_id, user_id, subject, client_name, phone, created_at in rows[:20]:
            lines.append(f"• #{request_id} | user {user_id} | {subject} | {client_name} | {phone} | {created_at[:16]}")

        await message.answer("\n".join(lines), reply_markup=admin_menu(lang))
        return

    if text == TEXTS[lang]["admin_premium_users_btn"]:
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        rows = get_premium_users()
        if not rows:
            await message.answer(TEXTS[lang]["admin_no_premium_users"], reply_markup=admin_menu(lang))
            return

        lines = [TEXTS[lang]["admin_premium_users_btn"] + ":"]

        lines = [TEXTS[lang]["admin_premium_users_btn"] + ":"]
        for user_id, premium_until in rows[:50]:
            lines.append(f"• {user_id} — {premium_until[:16]}")

        await message.answer("\n".join(lines), reply_markup=admin_menu(lang))
        return

    if text == TEXTS[lang]["admin_search_btn"]:
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        user_state[message.from_user.id] = "admin_search_wait"
        await message.answer(TEXTS[lang]["admin_search_prompt"], reply_markup=back_menu(lang))
        return

    if text == TEXTS[lang]["admin_reply_btn"]:
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        user_state[message.from_user.id] = "admin_reply_user_wait"
        await message.answer(TEXTS[lang]["admin_reply_prompt"], reply_markup=back_menu(lang))
        return

    if text == TEXTS[lang]["admin_balance_btn"]:
        if not is_admin_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        user_state[message.from_user.id] = "admin_balance_lookup_wait"
        await message.answer(TEXTS[lang]["admin_balance_lookup_prompt"], reply_markup=back_menu(lang))
        return

    if text == TEXTS[lang]["admin_panel_title"]:
        if is_admin_user(message.from_user.id):
            user_state[message.from_user.id] = "admin_panel"
            await message.answer(TEXTS[lang]["admin_panel_title"], reply_markup=admin_menu(lang))
            return

    if is_tutor_withdraw_button_text(text, message.from_user.id, lang):
        if not is_tutor_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        balance = get_tutor_balance(message.from_user.id)

        if balance < 1000:
            await message.answer(
                f"{TEXTS[lang]['tutor_withdraw_balance_info'].format(balance=balance)}\n"
                f"{TEXTS[lang]['tutor_withdraw_not_available']}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
            return

        user_state[message.from_user.id] = "tutor_withdraw_card_wait"
        await message.answer(
            f"{TEXTS[lang]['tutor_withdraw_balance_info'].format(balance=balance)}\n"
            f"{TEXTS[lang]['tutor_enter_card']}",
            reply_markup=back_menu(lang)
        )
        return

    if text == TEXTS[lang]["tutor_new_requests_btn"]:
        if not is_tutor_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        rows = get_unassigned_tutor_requests()
        if not rows:
            await message.answer(
                f"{TEXTS[lang]['tutor_no_new_requests']}\n\n{build_tutor_balance_info_text(message.from_user.id, lang)}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
            return

        for request_id, user_id, category, subject, client_name, phone, level, goal, preferred_time, lesson_format, created_at, payment_type, payment_amount in rows:
            payment_info = "-"
            if payment_amount and payment_amount > 0:
                payment_info = f"{payment_type or '-'} | {payment_amount}⭐"

            request_text = (
                f"{TEXTS[lang]['tutor_request_detail_title']} #{request_id}\n\n"
                f"{TEXTS[lang]['complaint_user_id']}: {user_id}\n"
                f"{TEXTS[lang]['category_label']}: {category or '-'}\n"
                f"{TEXTS[lang]['tutor_subject']}: {subject}\n"
                f"{TEXTS[lang]['tutor_name']}: {client_name}\n"
                f"{TEXTS[lang]['tutor_phone']}: {phone}\n"
                f"{TEXTS[lang]['level_label']}: {level or '-'}\n"
                f"{TEXTS[lang]['goal_label']}: {goal or '-'}\n"
                f"{TEXTS[lang]['preferred_time_label']}: {preferred_time or '-'}\n"
                f"{TEXTS[lang]['format_label']}: {lesson_format or '-'}\n"
                f"Payment: {payment_info}\n"
                f"{TEXTS[lang]['status_label']}: {TEXTS[lang]['request_status_new']}\n"
                f"Created: {created_at[:16]}"
            )
            await message.answer(request_text, reply_markup=build_take_request_keyboard(request_id, lang))
        await message.answer(build_tutor_balance_info_text(message.from_user.id, lang), reply_markup=tutor_menu(message.from_user.id, lang))
        return

    if text == TEXTS[lang]["tutor_my_requests_btn"]:
        if not is_tutor_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        rows = get_tutor_assigned_requests(message.from_user.id)
        if not rows:
            await message.answer(
                f"{TEXTS[lang]['tutor_no_my_requests']}\n\n{build_tutor_balance_info_text(message.from_user.id, lang)}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
            return

        await message.answer(
            TEXTS[lang]["tutor_my_requests_btn"] + ":\n\n" + build_tutor_balance_info_text(message.from_user.id, lang),
            reply_markup=build_tutor_requests_keyboard(rows, lang)
        )
        return

    if text == TEXTS[lang]["tutor_profile_btn"]:
        if not is_tutor_user(message.from_user.id):
            await message.answer(TEXTS[lang]["no_access"], reply_markup=main_menu(lang))
            return

        user_state[message.from_user.id] = "tutor_panel"
        await message.answer(
            build_tutor_panel_text(message.from_user.id, lang),
            reply_markup=tutor_menu(message.from_user.id, lang)
        )
        return

    if text == TEXTS[lang]["tutor_logout_btn"]:
        logout_tutor(message.from_user.id)
        user_temp.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["tutor_logout_success"], reply_markup=main_menu(lang))
        return

    if text == TEXTS[lang]["tutor_login_btn"]:
        user = get_user(message.from_user.id)
        user_phone = user.get("phone")
        current_name = user.get("full_name") or get_telegram_full_name(message.from_user) or f"user_{message.from_user.id}"

        if not user_phone:
            user_state[message.from_user.id] = "start_phone_wait"
            await message.answer(TEXTS[lang]["start_phone_request"], reply_markup=get_start_phone_menu(lang))
            return

        if login_tutor_by_phone(message.from_user.id, user_phone):
            user_state[message.from_user.id] = "tutor_panel"
            await message.answer(
                f"{TEXTS[lang]['tutor_auth_success']}\n\n{build_tutor_panel_text(message.from_user.id, lang)}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
        else:
            register_tutor_profile(message.from_user.id, current_name, user_phone)
            user_state[message.from_user.id] = "tutor_panel"
            await message.answer(
                f"{TEXTS[lang]['tutor_register_success']}\n\n{build_tutor_panel_text(message.from_user.id, lang)}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
        return

    await message.answer(TEXTS[lang]["main_menu_hint"], reply_markup=main_menu(lang))


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    state = user_state.get(message.from_user.id)

    if state == "start_phone_wait":
        phone = normalize_phone(message.contact.phone_number)
        contact_name_parts = [getattr(message.contact, "first_name", "") or "", getattr(message.contact, "last_name", "") or ""]
        contact_full_name = " ".join(part.strip() for part in contact_name_parts if part and part.strip()).strip()
        full_name = contact_full_name or get_telegram_full_name(message.from_user)

        set_user_phone(message.from_user.id, phone)
        set_user_full_name(message.from_user.id, full_name)
        set_user_language(message.from_user.id, detect_language_code(message.from_user.language_code), manual=False)

        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[lang]["start_phone_saved"], reply_markup=main_menu(lang))
        return


async def set_bot_commands():
    commands = [
        BotCommand("myprofile", "Мій акаунт"),
        BotCommand("premium", "Premium профіль"),
        BotCommand("complaint", "Підтримка / скарга"),
        BotCommand("language", "Змінити мову"),
        BotCommand("admin", "Вхід в Admin акаунт"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(_):
    global BOT_USERNAME
    init_db()
    ensure_user(OWNER_ID)
    add_admin(OWNER_ID)
    await set_bot_commands()

    try:
        me = await bot.get_me()
        BOT_USERNAME = me.username or ""
    except Exception as e:
        logging.warning(f"Не вдалося отримати username бота: {e}")

    try:
        await check_premium_reminders()
    except Exception as e:
        logging.warning(f"Помилка перевірки premium reminders: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
