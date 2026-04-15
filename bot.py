import json
import logging
import os
import re
import sqlite3
import urllib.parse
import urllib.request
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
    "payment_label": "Оплата",
    "created_label": "Створено",
    "sender_user_label": "Користувач",
    "sender_tutor_label": "Tutor",
    "withdraw_left_to_earn": "До виведення залишилось заробити: {remaining}⭐",
    "withdraw_already_available": "Виведення вже доступне.",
    "popular_subjects_category": "Популярні предмети",
    "reply_send_error": "❌ Не вдалося відправити повідомлення: {error}",
    "premium_invoice_title": "Оплата Premium профілю",
    "premium_invoice_description": "Необмежена кількість завдань на один місяць",
    "premium_invoice_label": "Premium профіль",
    "task_invoice_title": "Оплата одного завдання",
    "task_invoice_description": "Оплата за одне завдання",
    "task_invoice_label": "Одне завдання",
    "complex_invoice_title": "Оплата комплексної роботи",
    "complex_invoice_description": "Оплата за комплексне виконання роботи",
    "complex_invoice_label": "Комплексна робота",
    "payment_type_task_label": "Одне завдання",
    "payment_type_complex_label": "Комплексне виконання роботи",
    "payment_type_premium_label": "Преміум профіль",
    "tutor_subject_title": "📚 Вибери потрібний предмет",
    "categories_title": "📚 Вибери потрібний предмет",
})

TEXTS["ru"].update({
    "share_phone_btn": "📱 Поделиться номером",
    "payment_label": "Оплата",
    "created_label": "Создано",
    "sender_user_label": "Пользователь",
    "sender_tutor_label": "Tutor",
    "withdraw_left_to_earn": "До вывода осталось заработать: {remaining}⭐",
    "withdraw_already_available": "Вывод уже доступен.",
    "popular_subjects_category": "Популярные предметы",
    "reply_send_error": "❌ Не удалось отправить сообщение: {error}",
    "premium_invoice_title": "Оплата Premium профиля",
    "premium_invoice_description": "Неограниченное количество заданий на один месяц",
    "premium_invoice_label": "Premium профиль",
    "task_invoice_title": "Оплата одного задания",
    "task_invoice_description": "Оплата за одно задание",
    "task_invoice_label": "Одно задание",
    "complex_invoice_title": "Оплата комплексной работы",
    "complex_invoice_description": "Оплата за комплексное выполнение работы",
    "complex_invoice_label": "Комплексная работа",
    "payment_type_task_label": "Одно задание",
    "payment_type_complex_label": "Комплексное выполнение работы",
    "payment_type_premium_label": "Премиум профиль",
    "tutor_subject_title": "📚 Выбери нужный предмет",
    "categories_title": "📚 Выбери нужный предмет",
})

TEXTS["en"] = {
    "language_text": "👋 Choose the bot language",
    "main_menu_hint": "👋 Choose an action",
    "start_phone_request": "📱 To start using the bot, share your Telegram phone number.",
    "start_phone_saved": "✅ Phone number saved.",
    "share_phone_btn": "📱 Share phone number",
    "task": "Complete a task🙏",
    "tutor": "Need a tutor💪",
    "my_requests_btn": "📂 My requests",
    "support_btn": "🆘 Support",
    "menu_btn": "👤 My account",
    "back": "🏠 Main menu",
    "one": "Single task",
    "complex": "Complex assignment",
    "premium_profile": "Premium profile",
    "premium_profile_info": "For a full month, you get unlimited tasks in any school subject.",
    "profile_upgrade_btn": "🚀 Upgrade profile to Premium",
    "choose_service": "👇 Choose a service",
    "file_sent": "📩 File sent to the administrator.",
    "file_sent_to_tutor": "📩 File sent to the Tutor.",
    "no_payment": "❌ Payment is required first.",
    "send_file_now": "📎 Now you can send the file.",
    "pay_success_task": "✅ Payment of 250⭐ was successful.",
    "pay_success_complex": "✅ Payment of 500⭐ was successful.",
    "pay_success_premium_profile": "✅ Payment of 2500⭐ for the premium profile was successful.",
    "premium_profile_activated": "💎 Premium profile activated for 30 days.",
    "system_menu_title": "👤 My account",
    "my_profile_btn": "👤 My profile",
    "premium_menu_btn": "⭐ Premium profile",
    "tutor_login_btn": "🎓 Log in to Tutor account",
    "tutor_profile_btn": "📚 Tutor profile",
    "tutor_logout_btn": "🚪 Log out of Tutor profile",
    "tutor_logout_success": "✅ You logged out of the Tutor profile.",
    "admin_login_btn": "🔐 Log in to Admin account",
    "admin_profile_btn": "🛠 Admin profile",
    "admin_logout_btn": "🚪 Log out of admin profile",
    "admin_logout_success": "✅ You logged out of the admin profile.",
    "profile_title": "👤 My profile",
    "profile_role": "Profile type",
    "profile_language": "Bot language",
    "profile_status": "Status",
    "profile_until": "Premium active until",
    "profile_user": "User",
    "profile_admin": "Administrator",
    "profile_tutor": "Tutor",
    "profile_basic": "Basic profile",
    "profile_premium": "Premium profile",
    "payments_history_title": "💳 Payment history",
    "orders_history_title": "📦 Request history",
    "no_payments_history": "Payment history is empty so far.",
    "no_requests": "You do not have any requests yet.",
    "change_language_btn": "🌍 Change language",
    "complaint_sent": "✅ Message sent to the administrator.",
    "complaint_header": "🆘 New message",
    "complaint_user_id": "User ID",
    "complaint_username": "Username",
    "complaint_language": "Language",
    "complaint_profile": "Profile",
    "complaint_text_label": "Text",
    "support_text": "🆘 Send your question in one message and the administrator will receive it.",
    "ask_admin_login": "Enter administrator login:",
    "ask_admin_password": "Enter administrator password:",
    "admin_login_success": "✅ Administrator login successful.",
    "admin_login_fail": "❌ Incorrect login or password.",
    "admin_panel_title": "🛠 Admin panel",
    "admin_new_requests_btn": "📥 New requests",
    "admin_premium_users_btn": "💎 Premium users",
    "admin_search_btn": "🔎 Search",
    "admin_reply_btn": "💬 Reply to client",
    "admin_no_new_requests": "There are no new requests.",
    "admin_no_premium_users": "There are no active premium users.",
    "admin_search_prompt": "Enter the user ID:",
    "admin_reply_prompt": "Enter the user ID you want to reply to:",
    "admin_reply_text_prompt": "Enter the reply text for the user:",
    "admin_reply_sent": "✅ Message sent to the user.",
    "tutor_auth_success": "✅ Tutor login successful.",
    "tutor_register_success": "✅ Tutor profile created. Login completed.",
    "tutor_panel_title": "📚 Tutor panel",
    "tutor_panel_name": "👤 Tutor",
    "tutor_panel_balance": "💰 Balance",
    "tutor_panel_withdraw_status_ready": "✅ Withdrawal available",
    "tutor_panel_withdraw_status_wait": "⏳ You need {remaining}⭐ more before withdrawal",
    "tutor_new_requests_btn": "🆕 New requests",
    "tutor_my_requests_btn": "📂 Requests in progress",
    "tutor_no_new_requests": "There are no new requests for the Tutor.",
    "tutor_no_my_requests": "You do not have any requests in progress yet.",
    "tutor_take_request_btn": "✅ Take request",
    "tutor_take_success": "✅ Request taken into work.",
    "tutor_take_failed": "⚠️ This request has already been taken by another Tutor.",
    "tutor_request_taken_user": "✅ Your request has been taken by a Tutor. They can message you here in the chat.",
    "tutor_request_detail_title": "📄 Request",
    "tutor_write_user_btn": "💬 Message the user",
    "tutor_send_file_btn": "📎 Send file to the user",
    "tutor_reply_text_prompt": "Enter a message for the user:",
    "tutor_reply_text_sent": "✅ Message sent to the user.",
    "tutor_send_file_prompt": "Send one file for the user in a single message.",
    "tutor_send_file_sent": "✅ File sent to the user.",
    "request_files_title": "📎 Files for the request",
    "no_request_files": "There are no files for this request yet.",
    "file_from_user_caption": "📎 File from the user for request",
    "file_from_tutor_caption": "📎 File from the Tutor for request",
    "tutor_balance_label": "Balance",
    "tutor_withdraw_btn": "💸 Withdraw funds",
    "tutor_enter_card": "Enter the card number for withdrawal:",
    "tutor_withdraw_sent": "✅ Withdrawal request sent to the administrator.",
    "tutor_withdraw_not_available": "❌ Withdrawal is available only when the balance reaches 1000⭐.",
    "tutor_withdraw_balance_info": "💰 Current balance: {balance}⭐",
    "tutor_withdraw_request_title": "💸 Tutor wants to withdraw funds",
    "card_number_label": "Card number",
    "request_status_new": "New",
    "request_status_accepted": "Accepted",
    "request_status_in_progress": "In progress",
    "request_status_done": "Completed",
    "premium_expire_3days": "⏳ Your premium will expire in 3 days.",
    "premium_expired": "⚠️ Your premium has ended. The profile is basic again.",
    "confirm_btn": "✅ Confirm",
    "edit_btn": "✏️ Edit",
    "request_confirm_text": "Review the request details before sending:",
    "choose_valid_subject": "Please choose a subject using the buttons from the list.",
    "categories_title": "📚 Choose the required subject",
    "tutor_subject_title": "📚 Choose the required subject",
    "ask_level": "Enter your level or class:",
    "ask_goal": "Briefly describe your goal or problem:",
    "ask_time": "Write a convenient time for lessons:",
    "ask_format": "Specify the format: online / offline:",
    "tutor_request_sent": "✅ Request sent to the administrator. You will be contacted.",
    "tutor_request_header": "📚 New tutor request",
    "tutor_subject": "Subject",
    "tutor_name": "Name",
    "tutor_phone": "Phone",
    "phone_invalid": "❌ Please enter a valid phone number or press the button.",
    "no_access": "⛔ Access denied.",
    "user_not_found": "User not found.",
    "error_try_again": "Error. Please try again.",
    "admin_message_prefix": "💬 Message from administrator:\n\n",
    "new_order_prefix": "📥 New order",
    "user_id_label": "User ID",
    "username_label": "Username",
    "category_label": "Category",
    "level_label": "Level / class",
    "goal_label": "Goal / problem",
    "preferred_time_label": "Preferred time",
    "format_label": "Format",
    "status_label": "Status",
    "user_search_title": "🔎 User",
    "payment_label": "Payment",
    "created_label": "Created",
    "sender_user_label": "User",
    "sender_tutor_label": "Tutor",
    "withdraw_left_to_earn": "Left to earn before withdrawal: {remaining}⭐",
    "withdraw_already_available": "Withdrawal is already available.",
    "popular_subjects_category": "Popular subjects",
    "reply_send_error": "❌ Failed to send the message: {error}",
    "premium_invoice_title": "Premium profile payment",
    "premium_invoice_description": "Unlimited tasks for one month",
    "premium_invoice_label": "Premium profile",
    "task_invoice_title": "Single task payment",
    "task_invoice_description": "Payment for one task",
    "task_invoice_label": "Single task",
    "complex_invoice_title": "Complex work payment",
    "complex_invoice_description": "Payment for complex work",
    "complex_invoice_label": "Complex work",
    "payment_type_task_label": "Single task",
    "payment_type_complex_label": "Complex assignment",
    "payment_type_premium_label": "Premium profile",
}


for _lang_code, _extra_texts in {
    "ua": {
        "tutor_message_prefix": "💬 Tutor:\n\n",
        "file_generic_name": "файл",
    },
    "ru": {
        "tutor_message_prefix": "💬 Tutor:\n\n",
        "file_generic_name": "файл",
    },
    "en": {
        "tutor_message_prefix": "💬 Tutor:\n\n",
        "file_generic_name": "file",
    },
}.items():
    TEXTS[_lang_code].update(_extra_texts)

SUPPORTED_LANGUAGE_SPECS = [
    {"code": "ua", "button": "🇺🇦 Українська", "name": "Українська", "telegram_codes": ["uk", "ua"]},
    {"code": "ru", "button": "🇷🇺 Русский", "name": "Русский", "telegram_codes": ["ru"]},
    {"code": "en", "button": "🇬🇧 English", "name": "English", "telegram_codes": ["en"]},
    {"code": "de", "button": "🇩🇪 Deutsch", "name": "Deutsch", "telegram_codes": ["de"]},
    {"code": "fr", "button": "🇫🇷 Français", "name": "Français", "telegram_codes": ["fr"]},
    {"code": "it", "button": "🇮🇹 Italiano", "name": "Italiano", "telegram_codes": ["it"]},
    {"code": "es", "button": "🇪🇸 Español", "name": "Español", "telegram_codes": ["es"]},
    {"code": "pl", "button": "🇵🇱 Polski", "name": "Polski", "telegram_codes": ["pl"]},
    {"code": "ro", "button": "🇷🇴 Română", "name": "Română", "telegram_codes": ["ro"]},
    {"code": "nl", "button": "🇳🇱 Nederlands", "name": "Nederlands", "telegram_codes": ["nl"]},
    {"code": "tr", "button": "🇹🇷 Türkçe", "name": "Türkçe", "telegram_codes": ["tr"]},
    {"code": "pt", "button": "🇵🇹 Português", "name": "Português", "telegram_codes": ["pt"]},
    {"code": "el", "button": "🇬🇷 Ελληνικά", "name": "Ελληνικά", "telegram_codes": ["el"]},
    {"code": "cs", "button": "🇨🇿 Čeština", "name": "Čeština", "telegram_codes": ["cs"]},
    {"code": "sv", "button": "🇸🇪 Svenska", "name": "Svenska", "telegram_codes": ["sv"]},
    {"code": "hu", "button": "🇭🇺 Magyar", "name": "Magyar", "telegram_codes": ["hu"]},
    {"code": "be", "button": "🇧🇾 Беларуская", "name": "Беларуская", "telegram_codes": ["be"]},
    {"code": "bg", "button": "🇧🇬 Български", "name": "Български", "telegram_codes": ["bg"]},
    {"code": "sr", "button": "🇷🇸 Srpski", "name": "Srpski", "telegram_codes": ["sr"]},
    {"code": "da", "button": "🇩🇰 Dansk", "name": "Dansk", "telegram_codes": ["da"]},
    {"code": "fi", "button": "🇫🇮 Suomi", "name": "Suomi", "telegram_codes": ["fi"]},
    {"code": "sk", "button": "🇸🇰 Slovenčina", "name": "Slovenčina", "telegram_codes": ["sk"]},
    {"code": "no", "button": "🇳🇴 Norsk", "name": "Norsk", "telegram_codes": ["no", "nb", "nn"]},
    {"code": "hr", "button": "🇭🇷 Hrvatski", "name": "Hrvatski", "telegram_codes": ["hr"]},
    {"code": "bs", "button": "🇧🇦 Bosanski", "name": "Bosanski", "telegram_codes": ["bs"]},
    {"code": "sq", "button": "🇦🇱 Shqip", "name": "Shqip", "telegram_codes": ["sq"]},
    {"code": "lt", "button": "🇱🇹 Lietuvių", "name": "Lietuvių", "telegram_codes": ["lt"]},
    {"code": "sl", "button": "🇸🇮 Slovenščina", "name": "Slovenščina", "telegram_codes": ["sl"]},
    {"code": "lv", "button": "🇱🇻 Latviešu", "name": "Latviešu", "telegram_codes": ["lv"]},
    {"code": "et", "button": "🇪🇪 Eesti", "name": "Eesti", "telegram_codes": ["et"]},
    {"code": "mk", "button": "🇲🇰 Македонски", "name": "Македонски", "telegram_codes": ["mk"]},
    {"code": "mt", "button": "🇲🇹 Malti", "name": "Malti", "telegram_codes": ["mt"]},
    {"code": "is", "button": "🇮🇸 Íslenska", "name": "Íslenska", "telegram_codes": ["is"]},
    {"code": "ga", "button": "🇮🇪 Gaeilge", "name": "Gaeilge", "telegram_codes": ["ga"]},
    {"code": "cy", "button": "🏴 Cymraeg", "name": "Cymraeg", "telegram_codes": ["cy"]},
    {"code": "lb", "button": "🇱🇺 Lëtzebuergesch", "name": "Lëtzebuergesch", "telegram_codes": ["lb"]},
]

LANG_BUTTONS = {spec["button"]: spec["code"] for spec in SUPPORTED_LANGUAGE_SPECS}
LANG_NAMES = {spec["code"]: spec["name"] for spec in SUPPORTED_LANGUAGE_SPECS}
SUPPORTED_LANGUAGE_CODES = set(LANG_NAMES.keys())
TELEGRAM_LANGUAGE_CODE_MAP = {}
for spec in SUPPORTED_LANGUAGE_SPECS:
    for telegram_code in spec["telegram_codes"]:
        TELEGRAM_LANGUAGE_CODE_MAP[telegram_code] = spec["code"]

TRANSLATION_LANG_CODE_MAP = {
    "ua": "uk",
}
TRANSLATION_ENDPOINT = "https://translate.googleapis.com/translate_a/single"
TRANSLATION_BATCH_SIZE = 12
TRANSLATION_PROTECTED_TERMS = [
    "Tutor", "Admin", "Premium", "Telegram", "UTC", "XTR",
    "online", "offline", "User ID", "Username", "ID",
]
LANGUAGE_PACK_GENERATION_FAILED = set()
SUBJECT_TRANSLATIONS = {}
CATEGORY_TRANSLATIONS = {}

CATEGORY_BASE_LABELS = {
    "stem": "STEM",
    "languages": "Languages",
    "humanities": "Humanities",
    "business": "Business",
    "arts": "Arts",
    "primary": "Primary school",
}

CATEGORY_LABEL_OVERRIDES = {
    "ua": {
        "stem": "STEM",
        "languages": "Мови",
        "humanities": "Гуманітарні науки",
        "business": "Бізнес та економіка",
        "arts": "Мистецтво",
        "primary": "Початкова школа",
    },
    "ru": {
        "stem": "STEM",
        "languages": "Языки",
        "humanities": "Гуманитарные науки",
        "business": "Бизнес и экономика",
        "arts": "Искусство",
        "primary": "Начальная школа",
    },
    "en": CATEGORY_BASE_LABELS.copy(),
}

SUBJECTS = [
    {"id": "mathematics", "label": "Mathematics", "category": "stem"},
    {"id": "english", "label": "English", "category": "languages"},
    {"id": "chemistry", "label": "Chemistry", "category": "stem"},
    {"id": "biology", "label": "Biology", "category": "stem"},
    {"id": "physics", "label": "Physics", "category": "stem"},
    {"id": "computer_science", "label": "Computer Science", "category": "stem"},
    {"id": "native_language", "label": "Native Language & Literature", "category": "languages"},
    {"id": "german", "label": "German", "category": "languages"},
    {"id": "french", "label": "French", "category": "languages"},
    {"id": "spanish", "label": "Spanish", "category": "languages"},
    {"id": "history", "label": "History", "category": "humanities"},
    {"id": "geography", "label": "Geography", "category": "humanities"},
    {"id": "economics", "label": "Economics", "category": "business"},
    {"id": "statistics", "label": "Statistics", "category": "business"},
    {"id": "accounting", "label": "Accounting", "category": "business"},
    {"id": "music", "label": "Music", "category": "arts"},
    {"id": "art", "label": "Art", "category": "arts"},
    {"id": "primary_school", "label": "Primary School Support", "category": "primary"},
]

SUBJECTS_BY_ID = {item["id"]: item for item in SUBJECTS}
SUBJECT_ID_BY_ENGLISH_LABEL = {item["label"].lower(): item["id"] for item in SUBJECTS}
CATEGORY_ID_BY_ENGLISH_LABEL = {label.lower(): category_id for category_id, label in CATEGORY_BASE_LABELS.items()}

SUBJECT_LABEL_OVERRIDES = {
    "ua": {
        "mathematics": "Математика",
        "english": "Англійська мова",
        "chemistry": "Хімія",
        "biology": "Біологія",
        "physics": "Фізика",
        "computer_science": "Інформатика / програмування",
        "native_language": "Рідна мова та література",
        "german": "Німецька мова",
        "french": "Французька мова",
        "spanish": "Іспанська мова",
        "history": "Історія",
        "geography": "Географія",
        "economics": "Економіка",
        "statistics": "Статистика",
        "accounting": "Бухгалтерський облік",
        "music": "Музика",
        "art": "Образотворче мистецтво",
        "primary_school": "Початкова школа",
    },
    "ru": {
        "mathematics": "Математика",
        "english": "Английский язык",
        "chemistry": "Химия",
        "biology": "Биология",
        "physics": "Физика",
        "computer_science": "Информатика / программирование",
        "native_language": "Родной язык и литература",
        "german": "Немецкий язык",
        "french": "Французский язык",
        "spanish": "Испанский язык",
        "history": "История",
        "geography": "География",
        "economics": "Экономика",
        "statistics": "Статистика",
        "accounting": "Бухгалтерский учёт",
        "music": "Музыка",
        "art": "Изобразительное искусство",
        "primary_school": "Начальная школа",
    },
    "en": {item["id"]: item["label"] for item in SUBJECTS},
}


def normalize_language_code(language_code: str | None) -> str:
    if not language_code:
        return "ua"
    code = language_code.lower().replace("_", "-").strip()
    if code in SUPPORTED_LANGUAGE_CODES:
        return code
    if code in TELEGRAM_LANGUAGE_CODE_MAP:
        return TELEGRAM_LANGUAGE_CODE_MAP[code]
    base = code.split("-")[0]
    return TELEGRAM_LANGUAGE_CODE_MAP.get(base, "ua")


def _translation_target_code(lang: str) -> str:
    return TRANSLATION_LANG_CODE_MAP.get(lang, lang)


def _prepare_text_for_translation(text: str, segment_index: int):
    prepared = text
    restore_map = {}

    for match_index, match in enumerate(re.findall(r"\{[^{}]+\}", prepared)):
        token = f"__VAR_{segment_index}_{match_index}__"
        prepared = prepared.replace(match, token, 1)
        restore_map[token] = match

    for term_index, term in enumerate(TRANSLATION_PROTECTED_TERMS):
        token = f"__TERM_{segment_index}_{term_index}__"
        if term in prepared:
            prepared = prepared.replace(term, token)
            restore_map[token] = term

    return prepared, restore_map


def _restore_translated_text(text: str, restore_map: dict[str, str]) -> str:
    restored = text
    for token, original in restore_map.items():
        restored = restored.replace(token, original)
    return restored


def _call_google_translate(source_lang: str, target_lang: str, text: str):
    if not text:
        return ""

    params = urllib.parse.urlencode({
        "client": "gtx",
        "sl": source_lang,
        "tl": target_lang,
        "dt": "t",
        "q": text,
    })
    request = urllib.request.Request(
        f"{TRANSLATION_ENDPOINT}?{params}",
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read().decode("utf-8")
    except Exception as exc:
        logging.warning(f"Translation request failed for {target_lang}: {exc}")
        return None

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None

    translated_parts = []
    for item in data[0] if isinstance(data, list) and data else []:
        if isinstance(item, list) and item and item[0]:
            translated_parts.append(item[0])
    return "".join(translated_parts) or None


def _split_translated_batch(translated_text: str, expected_count: int):
    matches = list(re.finditer(r"\[\[\[(\d+)\]\]\]", translated_text))
    if len(matches) != expected_count:
        return []

    parts = [""] * expected_count
    for index, match in enumerate(matches):
        marker_value = int(match.group(1))
        if marker_value >= expected_count:
            return []
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(translated_text)
        parts[marker_value] = translated_text[start:end]

    return parts if all(part is not None for part in parts) else []


def _translate_batch(texts: list[str], target_lang: str, source_lang: str = "en"):
    if target_lang in {"ua", "ru", "en"}:
        return texts

    prepared_parts = []
    restore_maps = []
    for index, text in enumerate(texts):
        prepared_text, restore_map = _prepare_text_for_translation(text, index)
        prepared_parts.append(f"[[[{index}]]]{prepared_text}")
        restore_maps.append(restore_map)

    translated = _call_google_translate(source_lang, _translation_target_code(target_lang), "".join(prepared_parts))
    if translated:
        split_parts = _split_translated_batch(translated, len(texts))
        if len(split_parts) == len(texts):
            return [
                _restore_translated_text(split_parts[index].strip(), restore_maps[index]) or texts[index]
                for index in range(len(texts))
            ]

    result = []
    for index, text in enumerate(texts):
        prepared_text, restore_map = _prepare_text_for_translation(text, index)
        translated_text = _call_google_translate(source_lang, _translation_target_code(target_lang), prepared_text)
        if not translated_text:
            result.append(text)
            continue
        result.append(_restore_translated_text(translated_text.strip(), restore_map) or text)
    return result


def ensure_language_pack(lang: str) -> str:
    lang = normalize_language_code(lang)
    if lang in TEXTS:
        return lang

    if lang in LANGUAGE_PACK_GENERATION_FAILED:
        TEXTS[lang] = TEXTS["en"].copy()
        return lang

    base_keys = list(TEXTS["en"].keys())
    translated_pack = {}
    try:
        for offset in range(0, len(base_keys), TRANSLATION_BATCH_SIZE):
            chunk_keys = base_keys[offset: offset + TRANSLATION_BATCH_SIZE]
            chunk_values = [TEXTS["en"][key] for key in chunk_keys]
            chunk_translated = _translate_batch(chunk_values, lang)
            for key, translated_value, fallback in zip(chunk_keys, chunk_translated, chunk_values):
                translated_pack[key] = translated_value or fallback
    except Exception as exc:
        logging.warning(f"Failed to build language pack for {lang}: {exc}")
        LANGUAGE_PACK_GENERATION_FAILED.add(lang)
        TEXTS[lang] = TEXTS["en"].copy()
        return lang

    TEXTS[lang] = translated_pack or TEXTS["en"].copy()
    return lang


def ensure_subject_translations(lang: str):
    lang = normalize_language_code(lang)
    if lang in SUBJECT_TRANSLATIONS:
        return

    if lang in SUBJECT_LABEL_OVERRIDES:
        SUBJECT_TRANSLATIONS[lang] = SUBJECT_LABEL_OVERRIDES[lang].copy()
        return

    translated = _translate_batch([item["label"] for item in SUBJECTS], lang)
    SUBJECT_TRANSLATIONS[lang] = {
        item["id"]: translated[index] or item["label"]
        for index, item in enumerate(SUBJECTS)
    }


def ensure_category_translations(lang: str):
    lang = normalize_language_code(lang)
    if lang in CATEGORY_TRANSLATIONS:
        return

    if lang in CATEGORY_LABEL_OVERRIDES:
        CATEGORY_TRANSLATIONS[lang] = CATEGORY_LABEL_OVERRIDES[lang].copy()
        return

    category_ids = list(CATEGORY_BASE_LABELS.keys())
    translated = _translate_batch([CATEGORY_BASE_LABELS[category_id] for category_id in category_ids], lang)
    CATEGORY_TRANSLATIONS[lang] = {
        category_id: translated[index] or CATEGORY_BASE_LABELS[category_id]
        for index, category_id in enumerate(category_ids)
    }


def get_subject_label(subject_id: str, lang: str) -> str:
    lang = ensure_language_pack(lang)
    ensure_subject_translations(lang)
    return SUBJECT_TRANSLATIONS.get(lang, {}).get(subject_id, SUBJECTS_BY_ID.get(subject_id, {}).get("label", subject_id))


def get_category_label(category_id: str, lang: str) -> str:
    lang = ensure_language_pack(lang)
    ensure_category_translations(lang)
    return CATEGORY_TRANSLATIONS.get(lang, {}).get(category_id, CATEGORY_BASE_LABELS.get(category_id, category_id))


def get_subject_storage_label(subject_id: str) -> str:
    return SUBJECTS_BY_ID.get(subject_id, {}).get("label", subject_id)


def get_category_storage_label(category_id: str) -> str:
    return CATEGORY_BASE_LABELS.get(category_id, category_id)


def get_subject_id_by_label(label: str, lang: str):
    value = (label or "").strip().lower()
    if not value:
        return None

    for subject_id in SUBJECTS_BY_ID:
        if get_subject_label(subject_id, lang).lower() == value:
            return subject_id

    for overrides in SUBJECT_LABEL_OVERRIDES.values():
        for subject_id, subject_label in overrides.items():
            if subject_label.lower() == value:
                return subject_id

    return SUBJECT_ID_BY_ENGLISH_LABEL.get(value)


def resolve_subject_id_from_value(value: str):
    normalized = (value or "").strip().lower()
    if not normalized:
        return None

    if normalized in SUBJECT_ID_BY_ENGLISH_LABEL:
        return SUBJECT_ID_BY_ENGLISH_LABEL[normalized]

    for overrides in SUBJECT_LABEL_OVERRIDES.values():
        for subject_id, subject_label in overrides.items():
            if subject_label.lower() == normalized:
                return subject_id

    return None


def resolve_category_id_from_value(value: str):
    normalized = (value or "").strip().lower()
    if not normalized:
        return None

    if normalized in CATEGORY_ID_BY_ENGLISH_LABEL:
        return CATEGORY_ID_BY_ENGLISH_LABEL[normalized]

    for overrides in CATEGORY_LABEL_OVERRIDES.values():
        for category_id, category_label in overrides.items():
            if category_label.lower() == normalized:
                return category_id

    return None


def localize_subject_value(value: str, lang: str) -> str:
    subject_id = resolve_subject_id_from_value(value)
    if not subject_id:
        return value or "-"
    return get_subject_label(subject_id, lang)


def localize_category_value(value: str, lang: str) -> str:
    category_id = resolve_category_id_from_value(value)
    if not category_id:
        return value or "-"
    return get_category_label(category_id, lang)


def get_subject_category_id(subject_id: str) -> str:
    return SUBJECTS_BY_ID.get(subject_id, {}).get("category", "languages")


def get_payment_label(payment_type: str, lang: str) -> str:
    aliases = {
        "task": "task",
        "single_task": "task",
        "Одне завдання": "task",
        "Одно задание": "task",
        "Single task": "task",
        "complex": "complex",
        "Комплексне виконання роботи": "complex",
        "Комплексное выполнение работы": "complex",
        "Complex assignment": "complex",
        "premium_profile": "premium_profile",
        "Преміум профіль": "premium_profile",
        "Премиум профиль": "premium_profile",
        "Premium profile": "premium_profile",
    }
    normalized = aliases.get(payment_type, payment_type)
    if normalized == "task":
        return TEXTS[lang]["payment_type_task_label"]
    if normalized == "complex":
        return TEXTS[lang]["payment_type_complex_label"]
    if normalized == "premium_profile":
        return TEXTS[lang]["payment_type_premium_label"]
    return payment_type


def get_request_sender_label(sender_role: str, lang: str) -> str:
    if sender_role == "tutor":
        return TEXTS[lang]["sender_tutor_label"]
    return TEXTS[lang]["sender_user_label"]


async def send_payment_invoice(chat_id: int, lang: str, payment_type: str):
    lang = ensure_language_pack(lang)
    config = {
        "task": {
            "payload": "task_payment",
            "title_key": "task_invoice_title",
            "description_key": "task_invoice_description",
            "label_key": "task_invoice_label",
            "amount": 250,
            "start_parameter": "task",
        },
        "complex": {
            "payload": "complex_payment",
            "title_key": "complex_invoice_title",
            "description_key": "complex_invoice_description",
            "label_key": "complex_invoice_label",
            "amount": 500,
            "start_parameter": "complex",
        },
        "premium_profile": {
            "payload": "premium_profile_payment",
            "title_key": "premium_invoice_title",
            "description_key": "premium_invoice_description",
            "label_key": "premium_invoice_label",
            "amount": 2500,
            "start_parameter": "premium_profile",
        },
    }[payment_type]

    await bot.send_invoice(
        chat_id=chat_id,
        title=TEXTS[lang][config["title_key"]],
        description=TEXTS[lang][config["description_key"]],
        payload=config["payload"],
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=TEXTS[lang][config["label_key"]], amount=config["amount"])],
        start_parameter=config["start_parameter"],
    )

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


def get_tutor_withdraw_progress(tutor_user_id: int) -> tuple[int, int, int]:
    balance = get_tutor_balance(tutor_user_id)
    target = 1000
    remaining = max(0, target - balance)
    return balance, target, remaining


def get_tutor_withdraw_button_text(tutor_user_id: int, lang: str) -> str:
    lang = ensure_language_pack(lang)
    balance, target, _ = get_tutor_withdraw_progress(tutor_user_id)
    return f"{TEXTS[lang]['tutor_withdraw_btn']} {balance}/{target}⭐"


def is_tutor_withdraw_button_text(text_value: str, tutor_user_id: int, lang: str) -> bool:
    lang = ensure_language_pack(lang)
    return text_value == TEXTS[lang]['tutor_withdraw_btn'] or text_value == get_tutor_withdraw_button_text(tutor_user_id, lang)


def build_tutor_balance_info_text(tutor_user_id: int, lang: str) -> str:
    lang = ensure_language_pack(lang)
    balance, _, remaining = get_tutor_withdraw_progress(tutor_user_id)
    if remaining > 0:
        return (
            f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\n"
            f"{TEXTS[lang]['withdraw_left_to_earn'].format(remaining=remaining)}"
        )
    return (
        f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\n"
        f"{TEXTS[lang]['withdraw_already_available']}"
    )

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
                phone, full_name, premium_until, pending_payment,
                premium_remind_3days_sent, premium_expired_sent
            )
            VALUES (?, 'ua', 0, 0, 0, NULL, NULL, NULL, NULL, 0, 0)
        """, (user_id,))
        conn.commit()

    conn.close()


def get_user(user_id: int):
    ensure_user(user_id)
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, language, manual_language, is_admin, is_tutor,
               phone, full_name, premium_until, pending_payment,
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
        "premium_until": row[7],
        "pending_payment": row[8],
        "premium_remind_3days_sent": bool(row[9]),
        "premium_expired_sent": bool(row[10]),
    }


def detect_language_code(language_code: str):
    return ensure_language_pack(normalize_language_code(language_code))


def set_user_language(user_id: int, language: str, manual: bool = False):
    ensure_user(user_id)
    language = ensure_language_pack(normalize_language_code(language))
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


def resolve_user_language(message: types.Message):
    user_id = message.from_user.id
    ensure_user(user_id)
    sync_user_telegram_name(message.from_user)
    user = get_user(user_id)

    if user["manual_language"]:
        return ensure_language_pack(user["language"] or "ua")

    if message.from_user.language_code:
        detected = detect_language_code(message.from_user.language_code)
        set_user_language(user_id, detected, manual=False)
        return detected

    stored_language = user.get("language") or "ua"
    return ensure_language_pack(stored_language)


def get_user_interface_language(user_id: int) -> str:
    user = get_user(user_id)
    return ensure_language_pack(user.get("language") or "ua")


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
    lang = ensure_language_pack(lang)
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
    lang = ensure_language_pack(lang)
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
    ]

    if user.get("full_name"):
        lines.append(f"{TEXTS[lang]['tutor_name']}: {user['full_name']}")

    if user.get("phone"):
        lines.append(f"{TEXTS[lang]['tutor_phone']}: {user['phone']}")

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
            lines.append(f"• {get_payment_label(payment_type, lang)} — {amount_stars}⭐ ({created_at[:16]})")
    else:
        lines.append(TEXTS[lang]["no_payments_history"])

    requests = get_user_requests(user_id)
    lines.append("")
    lines.append(TEXTS[lang]["orders_history_title"] + ":")

    if requests:
        for request_id, subject, status_code, created_at in requests:
            lines.append(f"• #{request_id} | {localize_subject_value(subject, lang)} | {get_request_status_text(status_code, lang)} | {created_at[:16]}")
    else:
        lines.append(TEXTS[lang]["no_requests"])

    return "\n".join(lines)


def build_tutor_panel_text(user_id: int, lang: str):
    lang = ensure_language_pack(lang)
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
    lang = ensure_language_pack(lang)
    payment_part = "-"
    if request_data.get("payment_amount_stars", 0) > 0:
        payment_part = f"{get_payment_label(request_data.get('payment_type') or '-', lang)} | {request_data.get('payment_amount_stars')}⭐"

    return (
        f"{TEXTS[lang]['tutor_request_detail_title']} #{request_data['id']}\n\n"
        f"{TEXTS[lang]['complaint_user_id']}: {request_data['user_id']}\n"
        f"{TEXTS[lang]['category_label']}: {localize_category_value(request_data.get('category') or '-', lang)}\n"
        f"{TEXTS[lang]['tutor_subject']}: {localize_subject_value(request_data.get('subject') or '-', lang)}\n"
        f"{TEXTS[lang]['tutor_name']}: {request_data.get('client_name') or '-'}\n"
        f"{TEXTS[lang]['tutor_phone']}: {request_data.get('phone') or '-'}\n"
        f"{TEXTS[lang]['level_label']}: {request_data.get('level') or '-'}\n"
        f"{TEXTS[lang]['goal_label']}: {request_data.get('goal') or '-'}\n"
        f"{TEXTS[lang]['preferred_time_label']}: {request_data.get('preferred_time') or '-'}\n"
        f"{TEXTS[lang]['format_label']}: {request_data.get('lesson_format') or '-'}\n"
        f"{TEXTS[lang]['payment_label']}: {payment_part}\n"
        f"{TEXTS[lang]['status_label']}: {get_request_status_text(request_data.get('status', ''), lang)}"
    )

def main_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["task"])
    kb.row(TEXTS[lang]["tutor"])
    kb.row(TEXTS[lang]["support_btn"])
    kb.row(TEXTS[lang]["menu_btn"])
    return kb


def back_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["back"])
    return kb


def get_start_phone_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(TEXTS[lang].get("share_phone_btn", "📱 Поділитися номером"), request_contact=True))
    return kb


def system_menu(lang: str = "ua", is_admin: bool = False, is_tutor: bool = False):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    if is_tutor:
        kb.row(TEXTS[lang]["tutor_profile_btn"])
        kb.row(TEXTS[lang]["tutor_logout_btn"])
    else:
        kb.row(TEXTS[lang]["tutor_login_btn"])

    if is_admin:
        kb.row(TEXTS[lang]["admin_profile_btn"])
        kb.row(TEXTS[lang]["admin_logout_btn"])
    else:
        kb.row(TEXTS[lang]["admin_login_btn"])

    kb.row(TEXTS[lang]["premium_menu_btn"])
    kb.row(TEXTS[lang]["change_language_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def premium_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["back"])
    return kb


def profile_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["change_language_btn"])
    kb.row(TEXTS[lang]["profile_upgrade_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def admin_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["admin_new_requests_btn"])
    kb.row(TEXTS[lang]["admin_premium_users_btn"])
    kb.row(TEXTS[lang]["admin_search_btn"])
    kb.row(TEXTS[lang]["admin_reply_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def tutor_menu(user_id: int, lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["tutor_new_requests_btn"])
    kb.row(TEXTS[lang]["tutor_my_requests_btn"])
    kb.row(get_tutor_withdraw_button_text(user_id, lang))
    kb.row(TEXTS[lang]["back"])
    return kb


SUBJECT_CATEGORIES = {
    category_id: [item["id"] for item in SUBJECTS if item["category"] == category_id]
    for category_id in CATEGORY_BASE_LABELS
}


def get_language_keyboard(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    row = []
    for spec in SUPPORTED_LANGUAGE_SPECS:
        row.append(spec["button"])
        if len(row) == 2:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    kb.row(TEXTS[lang]["back"])
    return kb


def get_task_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["one"])
    kb.row(TEXTS[lang]["complex"])
    kb.row(TEXTS[lang]["premium_profile"])
    kb.row(TEXTS[lang]["back"])
    return kb


def get_tutor_categories_menu(lang: str = "ua"):
    return get_tutor_subjects_menu(lang=lang)


def get_tutor_subjects_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    row = []
    for item in SUBJECTS:
        row.append(get_subject_label(item["id"], lang))
        if len(row) == 2:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    kb.row(TEXTS[lang]["back"])
    return kb


def get_request_confirm_menu(lang: str = "ua"):
    lang = ensure_language_pack(lang)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["confirm_btn"], TEXTS[lang]["edit_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb

def build_take_request_keyboard(request_id: int, lang: str):
    lang = ensure_language_pack(lang)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        TEXTS[lang]["tutor_take_request_btn"],
        callback_data=f"take_request:{request_id}"
    ))
    return kb


def build_tutor_requests_keyboard(rows, lang: str):
    lang = ensure_language_pack(lang)
    kb = InlineKeyboardMarkup()
    for row in rows:
        request_id = row[0]
        subject = row[3]
        kb.add(InlineKeyboardButton(
            f"#{request_id} | {localize_subject_value(subject, lang)}",
            callback_data=f"open_tutor_request:{request_id}"
        ))
    return kb


def build_tutor_request_actions_keyboard(request_id: int, lang: str):
    lang = ensure_language_pack(lang)
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


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("take_request:"))
async def take_request_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = ensure_language_pack(get_user(user_id)["language"] or "ua")
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
            request_user_lang = get_user_interface_language(request_data["user_id"])
            await bot.send_message(request_data["user_id"], TEXTS[request_user_lang]["tutor_request_taken_user"])
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
    lang = ensure_language_pack(get_user(user_id)["language"] or "ua")
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
            sender_text = get_request_sender_label(sender_role, lang)
            lines.append(f"• {file_name or TEXTS[lang]['file_generic_name']} | {sender_text} | {created_at[:16]}")
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
    lang = ensure_language_pack(get_user(user_id)["language"] or "ua")
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
    lang = ensure_language_pack(get_user(user_id)["language"] or "ua")
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
    ensure_user(message.from_user.id)
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)

    user_state[message.from_user.id] = "start_phone_wait"
    await message.answer(TEXTS[lang]["start_phone_request"], reply_markup=get_start_phone_menu(lang))


@dp.message_handler(commands=["myprofile"])
async def cmd_myprofile(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "system_menu"
    await message.answer(
        TEXTS[lang]["system_menu_title"],
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
    user_state[message.from_user.id] = "premium_profile_screen"
    await message.answer(TEXTS[lang]["premium_profile_info"], reply_markup=premium_menu(lang))
    await send_payment_invoice(message.chat.id, lang, "premium_profile")


@dp.message_handler(commands=["complaint"])
async def cmd_complaint(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "complaint_wait"
    await message.answer(TEXTS[lang]["support_text"], reply_markup=back_menu(lang))


@dp.message_handler(commands=["language"])
async def cmd_language(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "language_menu"
    await message.answer(TEXTS[lang]["language_text"], reply_markup=get_language_keyboard(lang))


@dp.message_handler(commands=["admin"])
async def cmd_admin(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
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

    if payload == "task_payment":
        set_pending_payment(message.from_user.id, "task")
        add_payment(message.from_user.id, "task", 250)
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_task']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=back_menu(lang)
        )
        return

    if payload == "complex_payment":
        set_pending_payment(message.from_user.id, "complex")
        add_payment(message.from_user.id, "complex", 500)
        user_state[message.from_user.id] = "awaiting_file"
        await message.answer(
            f"{TEXTS[lang]['pay_success_complex']}\n\n{TEXTS[lang]['send_file_now']}",
            reply_markup=back_menu(lang)
        )
        return

    if payload == "premium_profile_payment":
        activate_premium(message.from_user.id, days=30)
        add_payment(message.from_user.id, "premium_profile", 2500)
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

        reply_user_lang = get_user_interface_language(reply_user_id)
        caption = f"{TEXTS[reply_user_lang]['file_from_tutor_caption']} #{request_id}"
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
            await message.answer(TEXTS[lang]["reply_send_error"].format(error=e), reply_markup=tutor_menu(message.from_user.id, lang))

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
            tutor_lang = get_user_interface_language(tutor_user_id)
            await bot.send_document(
                chat_id=tutor_user_id,
                document=message.document.file_id,
                caption=f"{TEXTS[tutor_lang]['file_from_user_caption']} #{request_id}"
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
    state = user_state.get(message.from_user.id, "main")
    text = message.text

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
        user_state[message.from_user.id] = "tutor_subject_wait"
        await message.answer(TEXTS[lang]["tutor_subject_title"], reply_markup=get_tutor_subjects_menu(lang))
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
            reply_user_lang = get_user_interface_language(reply_user_id)
            await bot.send_message(reply_user_id, f"{TEXTS[reply_user_lang]['tutor_message_prefix']}{text}")
            await message.answer(
                f"{TEXTS[lang]['tutor_reply_text_sent']}\n\n{build_tutor_panel_text(message.from_user.id, lang)}",
                reply_markup=tutor_menu(message.from_user.id, lang)
            )
        except Exception as e:
            await message.answer(TEXTS[lang]["reply_send_error"].format(error=e), reply_markup=tutor_menu(message.from_user.id, lang))

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
        user_state[message.from_user.id] = "tutor_subject_wait"
        await message.answer(TEXTS[lang]["tutor_subject_title"], reply_markup=get_tutor_subjects_menu(lang))
        return

    if state == "tutor_subject_wait":
        subject_id = get_subject_id_by_label(text, lang)

        if not subject_id:
            await message.answer(
                TEXTS[lang]["choose_valid_subject"],
                reply_markup=get_tutor_subjects_menu(lang)
            )
            return

        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["subject_id"] = subject_id
        user_temp[message.from_user.id]["subject"] = get_subject_storage_label(subject_id)
        user_temp[message.from_user.id]["category_id"] = get_subject_category_id(subject_id)
        user_temp[message.from_user.id]["category"] = get_category_storage_label(get_subject_category_id(subject_id))
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
            f"{TEXTS[lang]['category_label']}: {localize_category_value(d.get('category', '-'), lang)}\n"
            f"{TEXTS[lang]['tutor_subject']}: {localize_subject_value(d.get('subject', '-'), lang)}\n"
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
            user_state[message.from_user.id] = "tutor_subject_wait"
            user_temp[message.from_user.id] = {}
            await message.answer(TEXTS[lang]["tutor_subject_title"], reply_markup=get_tutor_subjects_menu(lang))
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
            f"{TEXTS[lang]['category_label']}: {localize_category_value(d.get('category', '-'), lang)}",
            f"{TEXTS[lang]['tutor_subject']}: {localize_subject_value(d.get('subject', '-'), lang)}",
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
        if target_user.get("full_name"):
            lines.append(f"{TEXTS[lang]['tutor_name']}: {target_user['full_name']}")

        if target_user.get("phone"):
            lines.append(f"{TEXTS[lang]['tutor_phone']}: {target_user['phone']}")

        if premium_until:
            lines.append(f"{TEXTS[lang]['profile_until']}: {premium_until[:16]}")

        lines.append("")
        lines.append(TEXTS[lang]["orders_history_title"] + ":")

        if requests:
            for subject, status_code, created_at in requests:
                lines.append(f"• {localize_subject_value(subject, lang)} | {get_request_status_text(status_code, lang)} | {created_at[:16]}")
        else:
            lines.append(TEXTS[lang]["no_requests"])

        lines.append("")
        lines.append(TEXTS[lang]["payments_history_title"] + ":")

        if payments:
            for payment_type, amount_stars, created_at in payments:
                lines.append(f"• {get_payment_label(payment_type, lang)} | {amount_stars}⭐ | {created_at[:16]}")
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
            reply_user_lang = get_user_interface_language(reply_user_id)
            await bot.send_message(reply_user_id, f"{TEXTS[reply_user_lang]['admin_message_prefix']}{text}")
            await message.answer(TEXTS[lang]["admin_reply_sent"], reply_markup=admin_menu(lang))
        except Exception as e:
            await message.answer(TEXTS[lang]["reply_send_error"].format(error=e), reply_markup=admin_menu(lang))

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
        await send_payment_invoice(message.chat.id, lang, "premium_profile")
        return

    if text == TEXTS[lang]["profile_upgrade_btn"]:
        user_state[message.from_user.id] = "premium_profile_screen"
        await message.answer(TEXTS[lang]["premium_profile_info"], reply_markup=premium_menu(lang))
        await send_payment_invoice(message.chat.id, lang, "premium_profile")
        return

    if text == TEXTS[lang]["one"]:
        await send_payment_invoice(message.chat.id, lang, "task")
        return

    if text == TEXTS[lang]["complex"]:
        await send_payment_invoice(message.chat.id, lang, "complex")
        return

    if text == TEXTS[lang]["premium_profile"]:
        user_state[message.from_user.id] = "task_menu"
        await message.answer(
            TEXTS[lang]["premium_profile_info"],
            reply_markup=get_task_menu(lang)
        )
        await send_payment_invoice(message.chat.id, lang, "premium_profile")
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
            lines.append(f"• #{request_id} | {TEXTS[lang]['profile_user']} {user_id} | {localize_subject_value(subject, lang)} | {client_name} | {phone} | {created_at[:16]}")

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
                payment_info = f"{get_payment_label(payment_type or '-', lang)} | {payment_amount}⭐"

            request_text = (
                f"{TEXTS[lang]['tutor_request_detail_title']} #{request_id}\n\n"
                f"{TEXTS[lang]['complaint_user_id']}: {user_id}\n"
                f"{TEXTS[lang]['category_label']}: {localize_category_value(category or '-', lang)}\n"
                f"{TEXTS[lang]['tutor_subject']}: {localize_subject_value(subject, lang)}\n"
                f"{TEXTS[lang]['tutor_name']}: {client_name}\n"
                f"{TEXTS[lang]['tutor_phone']}: {phone}\n"
                f"{TEXTS[lang]['level_label']}: {level or '-'}\n"
                f"{TEXTS[lang]['goal_label']}: {goal or '-'}\n"
                f"{TEXTS[lang]['preferred_time_label']}: {preferred_time or '-'}\n"
                f"{TEXTS[lang]['format_label']}: {lesson_format or '-'}\n"
                f"{TEXTS[lang]['payment_label']}: {payment_info}\n"
                f"{TEXTS[lang]['status_label']}: {TEXTS[lang]['request_status_new']}\n"
                f"{TEXTS[lang]['created_label']}: {created_at[:16]}"
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
    init_db()
    ensure_user(OWNER_ID)
    add_admin(OWNER_ID)
    await set_bot_commands()

    try:
        await check_premium_reminders()
    except Exception as e:
        logging.warning(f"Помилка перевірки premium reminders: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
