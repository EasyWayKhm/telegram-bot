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


LANGUAGE_DEFINITIONS = [
    [
        "ua",
        "🇺🇦",
        "Українська"
    ],
    [
        "ru",
        "🇷🇺",
        "Русский"
    ],
    [
        "en",
        "🇬🇧",
        "English"
    ],
    [
        "es",
        "🇪🇸",
        "Español"
    ],
    [
        "de",
        "🇩🇪",
        "Deutsch"
    ],
    [
        "fr",
        "🇫🇷",
        "Français"
    ],
    [
        "it",
        "🇮🇹",
        "Italiano"
    ],
    [
        "tr",
        "🇹🇷",
        "Türkçe"
    ],
    [
        "pl",
        "🇵🇱",
        "Polski"
    ],
    [
        "ro",
        "🇷🇴",
        "Română"
    ],
    [
        "nl",
        "🇳🇱",
        "Nederlands"
    ],
    [
        "el",
        "🇬🇷",
        "Ελληνικά"
    ],
    [
        "cs",
        "🇨🇿",
        "Čeština"
    ],
    [
        "pt",
        "🇵🇹",
        "Português"
    ],
    [
        "sv",
        "🇸🇪",
        "Svenska"
    ],
    [
        "hu",
        "🇭🇺",
        "Magyar"
    ],
    [
        "be",
        "🇧🇾",
        "Беларуская"
    ],
    [
        "bg",
        "🇧🇬",
        "Български"
    ],
    [
        "sr",
        "🇷🇸",
        "Srpski"
    ],
    [
        "da",
        "🇩🇰",
        "Dansk"
    ],
    [
        "fi",
        "🇫🇮",
        "Suomi"
    ],
    [
        "sk",
        "🇸🇰",
        "Slovenčina"
    ],
    [
        "no",
        "🇳🇴",
        "Norsk"
    ],
    [
        "hr",
        "🇭🇷",
        "Hrvatski"
    ],
    [
        "bs",
        "🇧🇦",
        "Bosanski"
    ],
    [
        "sq",
        "🇦🇱",
        "Shqip"
    ],
    [
        "lt",
        "🇱🇹",
        "Lietuvių"
    ],
    [
        "sl",
        "🇸🇮",
        "Slovenščina"
    ],
    [
        "lv",
        "🇱🇻",
        "Latviešu"
    ],
    [
        "et",
        "🇪🇪",
        "Eesti"
    ],
    [
        "mk",
        "🇲🇰",
        "Македонски"
    ],
    [
        "ka",
        "🇬🇪",
        "ქართული"
    ],
    [
        "hy",
        "🇦🇲",
        "Հայերեն"
    ],
    [
        "az",
        "🇦🇿",
        "Azərbaycanca"
    ],
    [
        "ca",
        "🇦🇩",
        "Català"
    ],
    [
        "is",
        "🇮🇸",
        "Íslenska"
    ],
    [
        "ga",
        "🇮🇪",
        "Gaeilge"
    ],
    [
        "mt",
        "🇲🇹",
        "Malti"
    ],
    [
        "lb",
        "🇱🇺",
        "Lëtzebuergesch"
    ]
]

TELEGRAM_LANGUAGE_ALIASES = {
    "uk": "ua",
    "uk-ua": "ua",
    "ua": "ua",
    "ru": "ru",
    "ru-ru": "ru",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "es": "es",
    "es-es": "es",
    "de": "de",
    "de-de": "de",
    "fr": "fr",
    "fr-fr": "fr",
    "it": "it",
    "it-it": "it",
    "tr": "tr",
    "tr-tr": "tr",
    "pl": "pl",
    "pl-pl": "pl",
    "ro": "ro",
    "ro-ro": "ro",
    "mo": "ro",
    "nl": "nl",
    "nl-nl": "nl",
    "el": "el",
    "el-gr": "el",
    "gr": "el",
    "cs": "cs",
    "cs-cz": "cs",
    "pt": "pt",
    "pt-pt": "pt",
    "pt-br": "pt",
    "sv": "sv",
    "sv-se": "sv",
    "hu": "hu",
    "hu-hu": "hu",
    "be": "be",
    "be-by": "be",
    "bg": "bg",
    "bg-bg": "bg",
    "sr": "sr",
    "sr-rs": "sr",
    "sr-latn": "sr",
    "sr-cyrl": "sr",
    "da": "da",
    "da-dk": "da",
    "fi": "fi",
    "fi-fi": "fi",
    "sk": "sk",
    "sk-sk": "sk",
    "no": "no",
    "nb": "no",
    "nn": "no",
    "nb-no": "no",
    "nn-no": "no",
    "no-no": "no",
    "hr": "hr",
    "hr-hr": "hr",
    "bs": "bs",
    "bs-ba": "bs",
    "sq": "sq",
    "sq-al": "sq",
    "lt": "lt",
    "lt-lt": "lt",
    "sl": "sl",
    "sl-si": "sl",
    "lv": "lv",
    "lv-lv": "lv",
    "et": "et",
    "et-ee": "et",
    "mk": "mk",
    "mk-mk": "mk",
    "ka": "ka",
    "ka-ge": "ka",
    "hy": "hy",
    "hy-am": "hy",
    "az": "az",
    "az-az": "az",
    "ca": "ca",
    "ca-es": "ca",
    "ca-ad": "ca",
    "is": "is",
    "is-is": "is",
    "ga": "ga",
    "ga-ie": "ga",
    "mt": "mt",
    "mt-mt": "mt",
    "lb": "lb",
    "lb-lu": "lb"
}

LANG_NAMES = {code: name for code, _, name in LANGUAGE_DEFINITIONS}
LANG_BUTTONS = {f"{flag} {name}": code for code, flag, name in LANGUAGE_DEFINITIONS}

BASE_TEXTS_EN = {
    "language_text": "👋 Choose the bot language",
    "main_menu_hint": "👋 Choose an action",
    "start_phone_request": "📱 To start using the bot, share your Telegram phone number.",
    "start_phone_saved": "✅ Phone number saved.",
    "share_phone_btn": "📱 Share phone number",
    "task": "Complete a task🙏",
    "tutor": "Need a tutor💪",
    "my_requests_btn": "📂 My requests",
    "support_btn": "🆘 Support",
    "menu_btn": "📋 Menu",
    "back": "🏠 Main menu",
    "one": "One task",
    "complex": "Comprehensive assignment help",
    "premium_profile": "Premium profile",
    "premium_profile_info": "For the whole month, you get unlimited tasks in any school subject.",
    "profile_upgrade_btn": "🚀 Upgrade profile to Premium",
    "choose_service": "👇 Choose a service",
    "file_sent": "📩 File sent to the administrator.",
    "file_sent_to_tutor": "📩 File sent to the tutor.",
    "no_payment": "❌ You need to pay first.",
    "send_file_now": "📎 Now you can send the file.",
    "pay_success_task": "✅ Payment of 250⭐ was successful.",
    "pay_success_complex": "✅ Payment of 500⭐ was successful.",
    "pay_success_premium_profile": "✅ Payment of 2500⭐ for the premium profile was successful.",
    "premium_profile_activated": "💎 Premium profile activated for 30 days.",
    "system_menu_title": "📋 Menu",
    "my_profile_btn": "👤 My profile",
    "premium_menu_btn": "⭐ Premium profile",
    "tutor_login_btn": "🎓 Tutor login",
    "tutor_profile_btn": "📚 Tutor profile",
    "tutor_logout_btn": "🚪 Log out from tutor profile",
    "tutor_logout_success": "✅ You logged out from the tutor profile.",
    "admin_login_btn": "🔐 Administrator login",
    "admin_profile_btn": "🛠 Admin profile",
    "admin_logout_btn": "🚪 Log out from admin profile",
    "admin_logout_success": "✅ You logged out from the admin profile.",
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
    "no_payments_history": "Payment history is empty for now.",
    "no_requests": "You have no requests yet.",
    "change_language_btn": "🌍 Change language",
    "complaint_sent": "✅ Message sent to the administrator.",
    "complaint_header": "🆘 New message",
    "complaint_user_id": "User ID",
    "complaint_username": "Username",
    "complaint_language": "Language",
    "complaint_profile": "Profile",
    "complaint_text_label": "Text",
    "support_text": "🆘 Write your question in one message, and the administrator will receive it.",
    "ask_admin_login": "Enter the administrator login:",
    "ask_admin_password": "Enter the administrator password:",
    "admin_login_success": "✅ Administrator login successful.",
    "admin_login_fail": "❌ Incorrect login or password.",
    "admin_panel_title": "🛠 Admin panel",
    "admin_new_requests_btn": "📥 New requests",
    "admin_premium_users_btn": "💎 Premium users",
    "admin_search_btn": "🔎 Search",
    "admin_reply_btn": "💬 Reply to user",
    "admin_no_new_requests": "There are no new requests.",
    "admin_no_premium_users": "There are no active premium users.",
    "admin_search_prompt": "Enter the user ID:",
    "admin_reply_prompt": "Enter the ID of the user you want to reply to:",
    "admin_reply_text_prompt": "Enter the reply text for the user:",
    "admin_reply_sent": "✅ Message sent to the user.",
    "tutor_auth_success": "✅ Tutor login successful.",
    "tutor_register_success": "✅ Tutor profile created. You are now logged in.",
    "tutor_panel_title": "📚 Tutor panel",
    "tutor_panel_name": "👤 Tutor",
    "tutor_panel_balance": "💰 Balance",
    "tutor_panel_withdraw_status_ready": "✅ Withdrawal available",
    "tutor_panel_withdraw_status_wait": "⏳ You need {remaining}⭐ more before withdrawal is available",
    "tutor_new_requests_btn": "🆕 New requests",
    "tutor_my_requests_btn": "📂 Requests in progress",
    "tutor_no_new_requests": "There are no new requests for tutors.",
    "tutor_no_my_requests": "You do not have any requests in progress yet.",
    "tutor_take_request_btn": "✅ Take request",
    "tutor_take_success": "✅ Request taken into work.",
    "tutor_take_failed": "⚠️ This request has already been taken by another tutor.",
    "tutor_request_taken_user": "✅ Your request has been taken by a tutor. They can message you here in the chat.",
    "tutor_request_detail_title": "📄 Request",
    "tutor_write_user_btn": "💬 Message the user",
    "tutor_send_file_btn": "📎 Send file to the user",
    "tutor_reply_text_prompt": "Enter a message for the user:",
    "tutor_reply_text_sent": "✅ Message sent to the user.",
    "tutor_send_file_prompt": "Send one file for the user in a single message.",
    "tutor_send_file_sent": "✅ File sent to the user.",
    "request_files_title": "📎 Files for this request",
    "no_request_files": "There are no files for this request yet.",
    "file_from_user_caption": "📎 File from the user for request",
    "file_from_tutor_caption": "📎 File from the tutor for request",
    "tutor_balance_label": "Balance",
    "tutor_withdraw_btn": "💸 Withdraw funds",
    "tutor_enter_card": "Enter the card number for withdrawal:",
    "tutor_withdraw_sent": "✅ Withdrawal request sent to the administrator.",
    "tutor_withdraw_not_available": "❌ Withdrawal is only available when your balance reaches 1000⭐.",
    "tutor_withdraw_balance_info": "💰 Current balance: {balance}⭐",
    "tutor_withdraw_request_title": "💸 Tutor wants to withdraw funds",
    "card_number_label": "Card number",
    "withdraw_left_to_earn": "You still need to earn {remaining}⭐ before withdrawal.",
    "withdraw_available_now": "Withdrawal is already available.",
    "request_status_new": "New",
    "request_status_accepted": "Accepted",
    "request_status_in_progress": "In progress",
    "request_status_done": "Completed",
    "premium_expire_3days": "⏳ Your premium will expire in 3 days.",
    "premium_expired": "⚠️ Your premium has ended. Your profile is basic again.",
    "confirm_btn": "✅ Confirm",
    "edit_btn": "✏️ Edit",
    "request_confirm_text": "Check the request details before sending:",
    "choose_valid_subject": "Please choose a subject using a button from the list.",
    "categories_title": "📚 Choose a subject category:",
    "tutor_subject_title": "Choose the subject you need a tutor for:",
    "ask_level": "Enter your level or grade:",
    "ask_goal": "Briefly describe your goal or problem:",
    "ask_time": "Enter a convenient time for lessons:",
    "ask_format": "Specify the format: online / offline:",
    "tutor_request_sent": "✅ Your request has been sent to the administrator. You will be contacted.",
    "tutor_request_header": "📚 New tutor request",
    "tutor_subject": "Subject",
    "tutor_name": "Name",
    "tutor_phone": "Phone",
    "phone_invalid": "❌ Please enter a valid phone number or press the button.",
    "no_access": "⛔ Access denied.",
    "user_not_found": "User not found.",
    "error_try_again": "Error. Please try again.",
    "admin_message_prefix": "💬 Message from the administrator:\n\n",
    "new_order_prefix": "📥 New order",
    "user_id_label": "User ID",
    "username_label": "Username",
    "category_label": "Category",
    "level_label": "Level / grade",
    "goal_label": "Goal / problem",
    "preferred_time_label": "Preferred time",
    "format_label": "Format",
    "status_label": "Status",
    "user_search_title": "🔎 User",
    "payment_label": "Payment",
    "created_label": "Created"
}

BASE_TEXTS_UA = {
    "language_text": "👋 Вибери мову бота",
    "main_menu_hint": "👋 Обери дію",
    "start_phone_request": "📱 Для початку користування ботом поділись своїм номером телефону Telegram.",
    "start_phone_saved": "✅ Номер телефону збережено.",
    "task": "Виконати завдання🙏",
    "tutor": "Потрібен репетитор💪",
    "my_requests_btn": "📂 Мої заявки",
    "support_btn": "🆘 Підтримка",
    "menu_btn": "📋 Меню",
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
    "system_menu_title": "📋 Меню",
    "my_profile_btn": "👤 Моя анкета",
    "premium_menu_btn": "⭐ Premium профіль",
    "tutor_login_btn": "🎓 Вхід Tutor",
    "tutor_profile_btn": "📚 Tutor профіль",
    "tutor_logout_btn": "🚪 Вихід з Tutor-профіля",
    "tutor_logout_success": "✅ Ти вийшов з Tutor-профіля.",
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
    "share_phone_btn": "📱 Поділитися номером",
    "withdraw_left_to_earn": "До виведення залишилось заробити: {remaining}⭐",
    "withdraw_available_now": "Виведення вже доступне.",
    "payment_label": "Оплата",
    "created_label": "Створено"
}

BASE_TEXTS_RU = {
    "language_text": "👋 Выберите язык бота",
    "main_menu_hint": "👋 Выберите действие",
    "start_phone_request": "📱 Для начала пользования ботом поделись своим номером телефона Telegram.",
    "start_phone_saved": "✅ Номер телефона сохранён.",
    "task": "Выполнить задание🙏",
    "tutor": "Нужен репетитор💪",
    "my_requests_btn": "📂 Мои заявки",
    "support_btn": "🆘 Поддержка",
    "menu_btn": "📋 Меню",
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
    "system_menu_title": "📋 Меню",
    "my_profile_btn": "👤 Моя анкета",
    "premium_menu_btn": "⭐ Premium профиль",
    "tutor_login_btn": "🎓 Вход Tutor",
    "tutor_profile_btn": "📚 Tutor профиль",
    "tutor_logout_btn": "🚪 Выход из Tutor-профиля",
    "tutor_logout_success": "✅ Ты вышел из Tutor-профиля.",
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
    "share_phone_btn": "📱 Поделиться номером",
    "withdraw_left_to_earn": "До вывода осталось заработать: {remaining}⭐",
    "withdraw_available_now": "Вывод уже доступен.",
    "payment_label": "Оплата",
    "created_label": "Создано"
}

LANGUAGE_MENU_OVERRIDES = {
    "es": {
        "language_text": "👋 Elige el idioma del bot",
        "main_menu_hint": "👋 Elige una acción",
        "share_phone_btn": "📱 Compartir número",
        "task": "Hacer una tarea🙏",
        "tutor": "Necesito un tutor💪",
        "support_btn": "🆘 Soporte",
        "menu_btn": "📋 Menú",
        "back": "🏠 Menú principal",
        "one": "Una tarea",
        "complex": "Ayuda integral con trabajos",
        "premium_profile": "Perfil Premium",
        "choose_service": "👇 Elige un servicio",
        "my_profile_btn": "👤 Mi perfil",
        "premium_menu_btn": "⭐ Perfil Premium",
        "tutor_login_btn": "🎓 Acceso tutor",
        "tutor_profile_btn": "📚 Perfil tutor",
        "tutor_logout_btn": "🚪 Salir del perfil de tutor",
        "admin_login_btn": "🔐 Acceso administrador",
        "admin_profile_btn": "🛠 Perfil admin",
        "admin_logout_btn": "🚪 Salir del perfil admin",
        "change_language_btn": "🌍 Cambiar idioma",
        "tutor_subject_title": "Elige la materia para la que necesitas un tutor:",
        "confirm_btn": "✅ Confirmar",
        "edit_btn": "✏️ Editar",
        "ask_level": "Indica tu nivel o curso:",
        "ask_goal": "Describe brevemente tu objetivo o problema:",
        "ask_time": "Indica un horario conveniente para las clases:",
        "ask_format": "Indica el formato: online / presencial:"
    },
    "de": {
        "language_text": "👋 Wähle die Botsprache",
        "main_menu_hint": "👋 Wähle eine Aktion",
        "share_phone_btn": "📱 Nummer teilen",
        "task": "Aufgabe erledigen🙏",
        "tutor": "Ich brauche einen Nachhilfelehrer💪",
        "support_btn": "🆘 Support",
        "menu_btn": "📋 Menü",
        "back": "🏠 Hauptmenü",
        "one": "Eine Aufgabe",
        "complex": "Umfassende Hilfe bei Arbeiten",
        "premium_profile": "Premium-Profil",
        "choose_service": "👇 Wähle einen Service",
        "my_profile_btn": "👤 Mein Profil",
        "premium_menu_btn": "⭐ Premium-Profil",
        "tutor_login_btn": "🎓 Tutor-Login",
        "tutor_profile_btn": "📚 Tutor-Profil",
        "tutor_logout_btn": "🚪 Aus dem Tutor-Profil abmelden",
        "admin_login_btn": "🔐 Admin-Login",
        "admin_profile_btn": "🛠 Admin-Profil",
        "admin_logout_btn": "🚪 Aus dem Admin-Profil abmelden",
        "change_language_btn": "🌍 Sprache ändern",
        "tutor_subject_title": "Wähle das Fach, für das du Nachhilfe brauchst:",
        "confirm_btn": "✅ Bestätigen",
        "edit_btn": "✏️ Bearbeiten",
        "ask_level": "Gib dein Niveau oder deine Klasse an:",
        "ask_goal": "Beschreibe kurz dein Ziel oder Problem:",
        "ask_time": "Gib eine passende Zeit für den Unterricht an:",
        "ask_format": "Format angeben: online / offline:"
    },
    "fr": {
        "language_text": "👋 Choisissez la langue du bot",
        "main_menu_hint": "👋 Choisissez une action",
        "share_phone_btn": "📱 Partager le numéro",
        "task": "Faire un devoir🙏",
        "tutor": "J’ai besoin d’un tuteur💪",
        "support_btn": "🆘 Support",
        "menu_btn": "📋 Menu",
        "back": "🏠 Menu principal",
        "one": "Un devoir",
        "complex": "Aide complète pour les travaux",
        "premium_profile": "Profil Premium",
        "choose_service": "👇 Choisissez un service",
        "my_profile_btn": "👤 Mon profil",
        "premium_menu_btn": "⭐ Profil Premium",
        "tutor_login_btn": "🎓 Connexion tuteur",
        "tutor_profile_btn": "📚 Profil tuteur",
        "tutor_logout_btn": "🚪 Quitter le profil tuteur",
        "admin_login_btn": "🔐 Connexion administrateur",
        "admin_profile_btn": "🛠 Profil admin",
        "admin_logout_btn": "🚪 Quitter le profil admin",
        "change_language_btn": "🌍 Changer de langue",
        "tutor_subject_title": "Choisissez la matière pour laquelle vous avez besoin d’un tuteur :",
        "confirm_btn": "✅ Confirmer",
        "edit_btn": "✏️ Modifier",
        "ask_level": "Indiquez votre niveau ou votre classe :",
        "ask_goal": "Décrivez brièvement votre objectif ou votre problème :",
        "ask_time": "Indiquez un horaire pratique pour les cours :",
        "ask_format": "Indiquez le format : en ligne / hors ligne :"
    },
    "it": {
        "language_text": "👋 Scegli la lingua del bot",
        "main_menu_hint": "👋 Scegli un’azione",
        "share_phone_btn": "📱 Condividi numero",
        "task": "Svolgere un compito🙏",
        "tutor": "Mi serve un tutor💪",
        "support_btn": "🆘 Supporto",
        "menu_btn": "📋 Menu",
        "back": "🏠 Menu principale",
        "one": "Un compito",
        "complex": "Aiuto completo con i lavori",
        "premium_profile": "Profilo Premium",
        "choose_service": "👇 Scegli un servizio",
        "my_profile_btn": "👤 Il mio profilo",
        "premium_menu_btn": "⭐ Profilo Premium",
        "tutor_login_btn": "🎓 Accesso tutor",
        "tutor_profile_btn": "📚 Profilo tutor",
        "tutor_logout_btn": "🚪 Esci dal profilo tutor",
        "admin_login_btn": "🔐 Accesso amministratore",
        "admin_profile_btn": "🛠 Profilo admin",
        "admin_logout_btn": "🚪 Esci dal profilo admin",
        "change_language_btn": "🌍 Cambia lingua",
        "tutor_subject_title": "Scegli la materia per cui ti serve un tutor:",
        "confirm_btn": "✅ Conferma",
        "edit_btn": "✏️ Modifica",
        "ask_level": "Indica il tuo livello o la tua classe:",
        "ask_goal": "Descrivi brevemente il tuo obiettivo o problema:",
        "ask_time": "Indica un orario comodo per le lezioni:",
        "ask_format": "Indica il formato: online / offline:"
    },
    "tr": {
        "language_text": "👋 Bot dilini seçin",
        "main_menu_hint": "👋 Bir işlem seçin",
        "share_phone_btn": "📱 Numarayı paylaş",
        "task": "Görevi yap🙏",
        "tutor": "Özel öğretmen lazım💪",
        "support_btn": "🆘 Destek",
        "menu_btn": "📋 Menü",
        "back": "🏠 Ana menü",
        "one": "Tek görev",
        "complex": "Kapsamlı ödev yardımı",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Bir hizmet seçin",
        "my_profile_btn": "👤 Profilim",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Eğitmen girişi",
        "tutor_profile_btn": "📚 Eğitmen profili",
        "tutor_logout_btn": "🚪 Eğitmen profilinden çık",
        "admin_login_btn": "🔐 Yönetici girişi",
        "admin_profile_btn": "🛠 Yönetici profili",
        "admin_logout_btn": "🚪 Yönetici profilinden çık",
        "change_language_btn": "🌍 Dili değiştir",
        "tutor_subject_title": "Hangi ders için öğretmene ihtiyacın olduğunu seç:",
        "confirm_btn": "✅ Onayla",
        "edit_btn": "✏️ Düzenle",
        "ask_level": "Seviyeni veya sınıfını yaz:",
        "ask_goal": "Hedefini veya sorununu kısaca yaz:",
        "ask_time": "Dersler için uygun zamanı yaz:",
        "ask_format": "Formatı belirt: çevrimiçi / yüz yüze:"
    },
    "pl": {
        "language_text": "👋 Wybierz język bota",
        "main_menu_hint": "👋 Wybierz działanie",
        "share_phone_btn": "📱 Udostępnij numer",
        "task": "Wykonać zadanie🙏",
        "tutor": "Potrzebuję korepetytora💪",
        "support_btn": "🆘 Wsparcie",
        "menu_btn": "📋 Menu",
        "back": "🏠 Menu główne",
        "one": "Jedno zadanie",
        "complex": "Kompleksowa pomoc w pracy",
        "premium_profile": "Profil Premium",
        "choose_service": "👇 Wybierz usługę",
        "my_profile_btn": "👤 Mój profil",
        "premium_menu_btn": "⭐ Profil Premium",
        "tutor_login_btn": "🎓 Logowanie tutora",
        "tutor_profile_btn": "📚 Profil tutora",
        "tutor_logout_btn": "🚪 Wyloguj z profilu tutora",
        "admin_login_btn": "🔐 Logowanie administratora",
        "admin_profile_btn": "🛠 Profil admina",
        "admin_logout_btn": "🚪 Wyloguj z profilu admina",
        "change_language_btn": "🌍 Zmień język",
        "tutor_subject_title": "Wybierz przedmiot, do którego potrzebujesz korepetytora:",
        "confirm_btn": "✅ Potwierdź",
        "edit_btn": "✏️ Edytuj",
        "ask_level": "Podaj swój poziom lub klasę:",
        "ask_goal": "Krótko opisz swój cel lub problem:",
        "ask_time": "Podaj dogodny czas zajęć:",
        "ask_format": "Podaj format: online / stacjonarnie:"
    },
    "ro": {
        "language_text": "👋 Alege limba botului",
        "main_menu_hint": "👋 Alege o acțiune",
        "share_phone_btn": "📱 Distribuie numărul",
        "task": "Rezolvă o temă🙏",
        "tutor": "Am nevoie de un meditator💪",
        "support_btn": "🆘 Suport",
        "menu_btn": "📋 Meniu",
        "back": "🏠 Meniul principal",
        "one": "O temă",
        "complex": "Ajutor complet pentru lucrări",
        "premium_profile": "Profil Premium",
        "choose_service": "👇 Alege un serviciu",
        "my_profile_btn": "👤 Profilul meu",
        "premium_menu_btn": "⭐ Profil Premium",
        "tutor_login_btn": "🎓 Autentificare tutor",
        "tutor_profile_btn": "📚 Profil tutor",
        "tutor_logout_btn": "🚪 Ieși din profilul de tutor",
        "admin_login_btn": "🔐 Autentificare administrator",
        "admin_profile_btn": "🛠 Profil admin",
        "admin_logout_btn": "🚪 Ieși din profilul admin",
        "change_language_btn": "🌍 Schimbă limba",
        "tutor_subject_title": "Alege materia pentru care ai nevoie de un tutor:",
        "confirm_btn": "✅ Confirmă",
        "edit_btn": "✏️ Editează",
        "ask_level": "Indică nivelul sau clasa ta:",
        "ask_goal": "Descrie pe scurt scopul sau problema ta:",
        "ask_time": "Indică un interval convenabil pentru lecții:",
        "ask_format": "Specifică formatul: online / offline:"
    },
    "nl": {
        "language_text": "👋 Kies de taal van de bot",
        "main_menu_hint": "👋 Kies een actie",
        "share_phone_btn": "📱 Nummer delen",
        "task": "Opdracht uitvoeren🙏",
        "tutor": "Ik heb een bijlesdocent nodig💪",
        "support_btn": "🆘 Support",
        "menu_btn": "📋 Menu",
        "back": "🏠 Hoofdmenu",
        "one": "Eén opdracht",
        "complex": "Uitgebreide hulp bij opdrachten",
        "premium_profile": "Premium-profiel",
        "choose_service": "👇 Kies een dienst",
        "my_profile_btn": "👤 Mijn profiel",
        "premium_menu_btn": "⭐ Premium-profiel",
        "tutor_login_btn": "🎓 Tutor-login",
        "tutor_profile_btn": "📚 Tutorprofiel",
        "tutor_logout_btn": "🚪 Uit tutorprofiel uitloggen",
        "admin_login_btn": "🔐 Admin-login",
        "admin_profile_btn": "🛠 Adminprofiel",
        "admin_logout_btn": "🚪 Uit adminprofiel uitloggen",
        "change_language_btn": "🌍 Taal wijzigen",
        "tutor_subject_title": "Kies het vak waarvoor je een tutor nodig hebt:",
        "confirm_btn": "✅ Bevestigen",
        "edit_btn": "✏️ Bewerken",
        "ask_level": "Geef je niveau of klas aan:",
        "ask_goal": "Beschrijf kort je doel of probleem:",
        "ask_time": "Geef een geschikt tijdstip voor de lessen aan:",
        "ask_format": "Geef de vorm aan: online / offline:"
    },
    "el": {
        "language_text": "👋 Επίλεξε τη γλώσσα του bot",
        "main_menu_hint": "👋 Επίλεξε ενέργεια",
        "share_phone_btn": "📱 Κοινοποίηση αριθμού",
        "task": "Εκτέλεση εργασίας🙏",
        "tutor": "Χρειάζομαι καθηγητή💪",
        "support_btn": "🆘 Υποστήριξη",
        "menu_btn": "📋 Μενού",
        "back": "🏠 Κεντρικό μενού",
        "one": "Μία εργασία",
        "complex": "Πλήρης βοήθεια σε εργασίες",
        "premium_profile": "Premium προφίλ",
        "choose_service": "👇 Επίλεξε υπηρεσία",
        "my_profile_btn": "👤 Το προφίλ μου",
        "premium_menu_btn": "⭐ Premium προφίλ",
        "tutor_login_btn": "🎓 Σύνδεση tutor",
        "tutor_profile_btn": "📚 Προφίλ tutor",
        "tutor_logout_btn": "🚪 Αποσύνδεση από το προφίλ tutor",
        "admin_login_btn": "🔐 Σύνδεση διαχειριστή",
        "admin_profile_btn": "🛠 Προφίλ admin",
        "admin_logout_btn": "🚪 Αποσύνδεση από το προφίλ admin",
        "change_language_btn": "🌍 Αλλαγή γλώσσας",
        "tutor_subject_title": "Επίλεξε το μάθημα για το οποίο χρειάζεσαι tutor:",
        "confirm_btn": "✅ Επιβεβαίωση",
        "edit_btn": "✏️ Επεξεργασία",
        "ask_level": "Γράψε το επίπεδο ή την τάξη σου:",
        "ask_goal": "Γράψε σύντομα τον στόχο ή το πρόβλημά σου:",
        "ask_time": "Γράψε μια βολική ώρα για τα μαθήματα:",
        "ask_format": "Όρισε μορφή: online / offline:"
    },
    "cs": {
        "language_text": "👋 Vyber jazyk bota",
        "main_menu_hint": "👋 Vyber akci",
        "share_phone_btn": "📱 Sdílet číslo",
        "task": "Splnit úkol🙏",
        "tutor": "Potřebuji lektora💪",
        "support_btn": "🆘 Podpora",
        "menu_btn": "📋 Menu",
        "back": "🏠 Hlavní menu",
        "one": "Jeden úkol",
        "complex": "Komplexní pomoc s prací",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Vyber službu",
        "my_profile_btn": "👤 Můj profil",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Přihlášení tutora",
        "tutor_profile_btn": "📚 Profil tutora",
        "tutor_logout_btn": "🚪 Odhlásit z profilu tutora",
        "admin_login_btn": "🔐 Přihlášení administrátora",
        "admin_profile_btn": "🛠 Admin profil",
        "admin_logout_btn": "🚪 Odhlásit z admin profilu",
        "change_language_btn": "🌍 Změnit jazyk",
        "tutor_subject_title": "Vyber předmět, ke kterému potřebuješ lektora:",
        "confirm_btn": "✅ Potvrdit",
        "edit_btn": "✏️ Upravit",
        "ask_level": "Uveď svou úroveň nebo třídu:",
        "ask_goal": "Stručně popiš svůj cíl nebo problém:",
        "ask_time": "Napiš vhodný čas na lekce:",
        "ask_format": "Uveď formát: online / offline:"
    },
    "pt": {
        "language_text": "👋 Escolhe o idioma do bot",
        "main_menu_hint": "👋 Escolhe uma ação",
        "share_phone_btn": "📱 Partilhar número",
        "task": "Fazer uma tarefa🙏",
        "tutor": "Preciso de um tutor💪",
        "support_btn": "🆘 Suporte",
        "menu_btn": "📋 Menu",
        "back": "🏠 Menu principal",
        "one": "Uma tarefa",
        "complex": "Ajuda completa com trabalhos",
        "premium_profile": "Perfil Premium",
        "choose_service": "👇 Escolhe um serviço",
        "my_profile_btn": "👤 O meu perfil",
        "premium_menu_btn": "⭐ Perfil Premium",
        "tutor_login_btn": "🎓 Login de tutor",
        "tutor_profile_btn": "📚 Perfil de tutor",
        "tutor_logout_btn": "🚪 Sair do perfil de tutor",
        "admin_login_btn": "🔐 Login de administrador",
        "admin_profile_btn": "🛠 Perfil admin",
        "admin_logout_btn": "🚪 Sair do perfil admin",
        "change_language_btn": "🌍 Alterar idioma",
        "tutor_subject_title": "Escolhe a disciplina para a qual precisas de tutor:",
        "confirm_btn": "✅ Confirmar",
        "edit_btn": "✏️ Editar",
        "ask_level": "Indica o teu nível ou ano:",
        "ask_goal": "Descreve brevemente o teu objetivo ou problema:",
        "ask_time": "Indica um horário conveniente para as aulas:",
        "ask_format": "Indica o formato: online / presencial:"
    },
    "sv": {
        "language_text": "👋 Välj botspråk",
        "main_menu_hint": "👋 Välj en åtgärd",
        "share_phone_btn": "📱 Dela nummer",
        "task": "Göra en uppgift🙏",
        "tutor": "Jag behöver en lärare💪",
        "support_btn": "🆘 Support",
        "menu_btn": "📋 Meny",
        "back": "🏠 Huvudmeny",
        "one": "En uppgift",
        "complex": "Omfattande hjälp med arbeten",
        "premium_profile": "Premiumprofil",
        "choose_service": "👇 Välj en tjänst",
        "my_profile_btn": "👤 Min profil",
        "premium_menu_btn": "⭐ Premiumprofil",
        "tutor_login_btn": "🎓 Tutorinloggning",
        "tutor_profile_btn": "📚 Tutorprofil",
        "tutor_logout_btn": "🚪 Logga ut från tutorprofilen",
        "admin_login_btn": "🔐 Admininloggning",
        "admin_profile_btn": "🛠 Adminprofil",
        "admin_logout_btn": "🚪 Logga ut från adminprofilen",
        "change_language_btn": "🌍 Byt språk",
        "tutor_subject_title": "Välj ämnet du behöver en tutor i:",
        "confirm_btn": "✅ Bekräfta",
        "edit_btn": "✏️ Redigera",
        "ask_level": "Ange din nivå eller klass:",
        "ask_goal": "Beskriv kort ditt mål eller problem:",
        "ask_time": "Ange en lämplig tid för lektioner:",
        "ask_format": "Ange format: online / offline:"
    },
    "hu": {
        "language_text": "👋 Válaszd ki a bot nyelvét",
        "main_menu_hint": "👋 Válassz műveletet",
        "share_phone_btn": "📱 Szám megosztása",
        "task": "Feladat megoldása🙏",
        "tutor": "Korrepetitorra van szükségem💪",
        "support_btn": "🆘 Támogatás",
        "menu_btn": "📋 Menü",
        "back": "🏠 Főmenü",
        "one": "Egy feladat",
        "complex": "Komplex segítség a munkákhoz",
        "premium_profile": "Prémium profil",
        "choose_service": "👇 Válassz szolgáltatást",
        "my_profile_btn": "👤 Profilom",
        "premium_menu_btn": "⭐ Prémium profil",
        "tutor_login_btn": "🎓 Tutor bejelentkezés",
        "tutor_profile_btn": "📚 Tutor profil",
        "tutor_logout_btn": "🚪 Kilépés a tutor profilból",
        "admin_login_btn": "🔐 Admin bejelentkezés",
        "admin_profile_btn": "🛠 Admin profil",
        "admin_logout_btn": "🚪 Kilépés az admin profilból",
        "change_language_btn": "🌍 Nyelv módosítása",
        "tutor_subject_title": "Válaszd ki a tantárgyat, amelyhez tutort keresel:",
        "confirm_btn": "✅ Megerősítés",
        "edit_btn": "✏️ Szerkesztés",
        "ask_level": "Add meg a szintedet vagy osztályodat:",
        "ask_goal": "Röviden írd le a célodat vagy problémádat:",
        "ask_time": "Írj egy megfelelő időpontot az órákhoz:",
        "ask_format": "Add meg a formátumot: online / offline:"
    },
    "be": {
        "language_text": "👋 Абяры мову бота",
        "main_menu_hint": "👋 Абяры дзеянне",
        "share_phone_btn": "📱 Падзяліцца нумарам",
        "task": "Выканаць заданне🙏",
        "tutor": "Патрэбен рэпетытар💪",
        "support_btn": "🆘 Падтрымка",
        "menu_btn": "📋 Меню",
        "back": "🏠 Галоўнае меню",
        "one": "Адно заданне",
        "complex": "Комплексная дапамога з работай",
        "premium_profile": "Premium профіль",
        "choose_service": "👇 Абяры паслугу",
        "my_profile_btn": "👤 Мой профіль",
        "premium_menu_btn": "⭐ Premium профіль",
        "tutor_login_btn": "🎓 Уваход Tutor",
        "tutor_profile_btn": "📚 Tutor профіль",
        "tutor_logout_btn": "🚪 Выйсці з Tutor-профілю",
        "admin_login_btn": "🔐 Уваход адміністратара",
        "admin_profile_btn": "🛠 Admin профіль",
        "admin_logout_btn": "🚪 Выйсці з admin-профілю",
        "change_language_btn": "🌍 Змяніць мову",
        "tutor_subject_title": "Абяры прадмет, па якім табе патрэбны рэпетытар:",
        "confirm_btn": "✅ Пацвердзіць",
        "edit_btn": "✏️ Рэдагаваць",
        "ask_level": "Пакажы свой узровень або клас:",
        "ask_goal": "Коратка апішы сваю мэту або праблему:",
        "ask_time": "Напішы зручны час для заняткаў:",
        "ask_format": "Пакажы фармат: анлайн / афлайн:"
    },
    "bg": {
        "language_text": "👋 Избери езика на бота",
        "main_menu_hint": "👋 Избери действие",
        "share_phone_btn": "📱 Сподели номер",
        "task": "Изпълни задача🙏",
        "tutor": "Трябва ми преподавател💪",
        "support_btn": "🆘 Поддръжка",
        "menu_btn": "📋 Меню",
        "back": "🏠 Главно меню",
        "one": "Една задача",
        "complex": "Пълна помощ по работа",
        "premium_profile": "Premium профил",
        "choose_service": "👇 Избери услуга",
        "my_profile_btn": "👤 Моят профил",
        "premium_menu_btn": "⭐ Premium профил",
        "tutor_login_btn": "🎓 Вход Tutor",
        "tutor_profile_btn": "📚 Tutor профил",
        "tutor_logout_btn": "🚪 Изход от Tutor профила",
        "admin_login_btn": "🔐 Вход администратор",
        "admin_profile_btn": "🛠 Admin профил",
        "admin_logout_btn": "🚪 Изход от admin профила",
        "change_language_btn": "🌍 Смени езика",
        "tutor_subject_title": "Избери предмета, за който ти трябва преподавател:",
        "confirm_btn": "✅ Потвърди",
        "edit_btn": "✏️ Редактирай",
        "ask_level": "Напиши нивото или класа си:",
        "ask_goal": "Опиши накратко целта или проблема си:",
        "ask_time": "Напиши удобно време за уроци:",
        "ask_format": "Посочи формат: онлайн / офлайн:"
    },
    "sr": {
        "language_text": "👋 Izaberi jezik bota",
        "main_menu_hint": "👋 Izaberi akciju",
        "share_phone_btn": "📱 Podeli broj",
        "task": "Uraditi zadatak🙏",
        "tutor": "Potreban mi je tutor💪",
        "support_btn": "🆘 Podrška",
        "menu_btn": "📋 Meni",
        "back": "🏠 Glavni meni",
        "one": "Jedan zadatak",
        "complex": "Kompletna pomoć za radove",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Izaberi uslugu",
        "my_profile_btn": "👤 Moj profil",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Tutor prijava",
        "tutor_profile_btn": "📚 Tutor profil",
        "tutor_logout_btn": "🚪 Odjava sa tutor profila",
        "admin_login_btn": "🔐 Admin prijava",
        "admin_profile_btn": "🛠 Admin profil",
        "admin_logout_btn": "🚪 Odjava sa admin profila",
        "change_language_btn": "🌍 Promeni jezik",
        "tutor_subject_title": "Izaberi predmet za koji ti je potreban tutor:",
        "confirm_btn": "✅ Potvrdi",
        "edit_btn": "✏️ Izmeni",
        "ask_level": "Upiši svoj nivo ili razred:",
        "ask_goal": "Kratko opiši svoj cilj ili problem:",
        "ask_time": "Napiši vreme koje ti odgovara za časove:",
        "ask_format": "Navedi format: online / offline:"
    },
    "da": {
        "language_text": "👋 Vælg botsprog",
        "main_menu_hint": "👋 Vælg en handling",
        "share_phone_btn": "📱 Del nummer",
        "task": "Udfør en opgave🙏",
        "tutor": "Jeg har brug for en tutor💪",
        "support_btn": "🆘 Support",
        "menu_btn": "📋 Menu",
        "back": "🏠 Hovedmenu",
        "one": "Én opgave",
        "complex": "Omfattende hjælp til opgaver",
        "premium_profile": "Premium-profil",
        "choose_service": "👇 Vælg en service",
        "my_profile_btn": "👤 Min profil",
        "premium_menu_btn": "⭐ Premium-profil",
        "tutor_login_btn": "🎓 Tutor-login",
        "tutor_profile_btn": "📚 Tutorprofil",
        "tutor_logout_btn": "🚪 Log ud af tutorprofilen",
        "admin_login_btn": "🔐 Admin-login",
        "admin_profile_btn": "🛠 Adminprofil",
        "admin_logout_btn": "🚪 Log ud af adminprofilen",
        "change_language_btn": "🌍 Skift sprog",
        "tutor_subject_title": "Vælg det fag, du har brug for en tutor til:",
        "confirm_btn": "✅ Bekræft",
        "edit_btn": "✏️ Rediger",
        "ask_level": "Angiv dit niveau eller din klasse:",
        "ask_goal": "Beskriv kort dit mål eller problem:",
        "ask_time": "Angiv et passende tidspunkt for lektioner:",
        "ask_format": "Angiv format: online / offline:"
    },
    "fi": {
        "language_text": "👋 Valitse botin kieli",
        "main_menu_hint": "👋 Valitse toiminto",
        "share_phone_btn": "📱 Jaa numero",
        "task": "Tee tehtävä🙏",
        "tutor": "Tarvitsen tutorin💪",
        "support_btn": "🆘 Tuki",
        "menu_btn": "📋 Valikko",
        "back": "🏠 Päävalikko",
        "one": "Yksi tehtävä",
        "complex": "Laaja apu tehtäviin",
        "premium_profile": "Premium-profiili",
        "choose_service": "👇 Valitse palvelu",
        "my_profile_btn": "👤 Profiilini",
        "premium_menu_btn": "⭐ Premium-profiili",
        "tutor_login_btn": "🎓 Tutor-kirjautuminen",
        "tutor_profile_btn": "📚 Tutor-profiili",
        "tutor_logout_btn": "🚪 Kirjaudu ulos tutor-profiilista",
        "admin_login_btn": "🔐 Ylläpitäjän kirjautuminen",
        "admin_profile_btn": "🛠 Admin-profiili",
        "admin_logout_btn": "🚪 Kirjaudu ulos admin-profiilista",
        "change_language_btn": "🌍 Vaihda kieltä",
        "tutor_subject_title": "Valitse aine, johon tarvitset tutorin:",
        "confirm_btn": "✅ Vahvista",
        "edit_btn": "✏️ Muokkaa",
        "ask_level": "Kirjoita tasosi tai luokkasi:",
        "ask_goal": "Kuvaa lyhyesti tavoitteesi tai ongelmasi:",
        "ask_time": "Kirjoita sopiva aika tunneille:",
        "ask_format": "Määritä muoto: online / offline:"
    },
    "sk": {
        "language_text": "👋 Vyber jazyk bota",
        "main_menu_hint": "👋 Vyber akciu",
        "share_phone_btn": "📱 Zdieľať číslo",
        "task": "Splniť úlohu🙏",
        "tutor": "Potrebujem lektora💪",
        "support_btn": "🆘 Podpora",
        "menu_btn": "📋 Menu",
        "back": "🏠 Hlavné menu",
        "one": "Jedna úloha",
        "complex": "Komplexná pomoc s prácou",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Vyber službu",
        "my_profile_btn": "👤 Môj profil",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Prihlásenie tutora",
        "tutor_profile_btn": "📚 Profil tutora",
        "tutor_logout_btn": "🚪 Odhlásiť sa z profilu tutora",
        "admin_login_btn": "🔐 Prihlásenie administrátora",
        "admin_profile_btn": "🛠 Admin profil",
        "admin_logout_btn": "🚪 Odhlásiť sa z admin profilu",
        "change_language_btn": "🌍 Zmeniť jazyk",
        "tutor_subject_title": "Vyber predmet, na ktorý potrebuješ lektora:",
        "confirm_btn": "✅ Potvrdiť",
        "edit_btn": "✏️ Upraviť",
        "ask_level": "Uveď svoju úroveň alebo ročník:",
        "ask_goal": "Stručne opíš svoj cieľ alebo problém:",
        "ask_time": "Napíš vhodný čas na hodiny:",
        "ask_format": "Uveď formát: online / offline:"
    },
    "no": {
        "language_text": "👋 Velg botspråk",
        "main_menu_hint": "👋 Velg en handling",
        "share_phone_btn": "📱 Del nummer",
        "task": "Utfør en oppgave🙏",
        "tutor": "Jeg trenger en lærer💪",
        "support_btn": "🆘 Støtte",
        "menu_btn": "📋 Meny",
        "back": "🏠 Hovedmeny",
        "one": "Én oppgave",
        "complex": "Omfattende hjelp med oppgaver",
        "premium_profile": "Premium-profil",
        "choose_service": "👇 Velg en tjeneste",
        "my_profile_btn": "👤 Min profil",
        "premium_menu_btn": "⭐ Premium-profil",
        "tutor_login_btn": "🎓 Tutor-innlogging",
        "tutor_profile_btn": "📚 Tutorprofil",
        "tutor_logout_btn": "🚪 Logg ut av tutorprofilen",
        "admin_login_btn": "🔐 Admin-innlogging",
        "admin_profile_btn": "🛠 Adminprofil",
        "admin_logout_btn": "🚪 Logg ut av adminprofilen",
        "change_language_btn": "🌍 Bytt språk",
        "tutor_subject_title": "Velg faget du trenger en tutor i:",
        "confirm_btn": "✅ Bekreft",
        "edit_btn": "✏️ Rediger",
        "ask_level": "Oppgi nivå eller klasse:",
        "ask_goal": "Beskriv kort målet eller problemet ditt:",
        "ask_time": "Skriv et passende tidspunkt for timene:",
        "ask_format": "Oppgi format: online / offline:"
    },
    "hr": {
        "language_text": "👋 Odaberi jezik bota",
        "main_menu_hint": "👋 Odaberi radnju",
        "share_phone_btn": "📱 Podijeli broj",
        "task": "Izvrši zadatak🙏",
        "tutor": "Trebam instruktora💪",
        "support_btn": "🆘 Podrška",
        "menu_btn": "📋 Izbornik",
        "back": "🏠 Glavni izbornik",
        "one": "Jedan zadatak",
        "complex": "Sveobuhvatna pomoć za radove",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Odaberi uslugu",
        "my_profile_btn": "👤 Moj profil",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Prijava tutora",
        "tutor_profile_btn": "📚 Tutor profil",
        "tutor_logout_btn": "🚪 Odjava s tutor profila",
        "admin_login_btn": "🔐 Admin prijava",
        "admin_profile_btn": "🛠 Admin profil",
        "admin_logout_btn": "🚪 Odjava s admin profila",
        "change_language_btn": "🌍 Promijeni jezik",
        "tutor_subject_title": "Odaberi predmet za koji ti treba instruktor:",
        "confirm_btn": "✅ Potvrdi",
        "edit_btn": "✏️ Uredi",
        "ask_level": "Upiši svoju razinu ili razred:",
        "ask_goal": "Kratko opiši svoj cilj ili problem:",
        "ask_time": "Napiši odgovarajuće vrijeme za nastavu:",
        "ask_format": "Navedi format: online / offline:"
    },
    "bs": {
        "language_text": "👋 Izaberi jezik bota",
        "main_menu_hint": "👋 Izaberi akciju",
        "share_phone_btn": "📱 Podijeli broj",
        "task": "Uraditi zadatak🙏",
        "tutor": "Treba mi instruktor💪",
        "support_btn": "🆘 Podrška",
        "menu_btn": "📋 Meni",
        "back": "🏠 Glavni meni",
        "one": "Jedan zadatak",
        "complex": "Kompletna pomoć za radove",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Izaberi uslugu",
        "my_profile_btn": "👤 Moj profil",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Tutor prijava",
        "tutor_profile_btn": "📚 Tutor profil",
        "tutor_logout_btn": "🚪 Odjava sa tutor profila",
        "admin_login_btn": "🔐 Admin prijava",
        "admin_profile_btn": "🛠 Admin profil",
        "admin_logout_btn": "🚪 Odjava sa admin profila",
        "change_language_btn": "🌍 Promijeni jezik",
        "tutor_subject_title": "Izaberi predmet za koji ti treba instruktor:",
        "confirm_btn": "✅ Potvrdi",
        "edit_btn": "✏️ Uredi",
        "ask_level": "Upiši svoj nivo ili razred:",
        "ask_goal": "Kratko opiši svoj cilj ili problem:",
        "ask_time": "Napiši odgovarajuće vrijeme za časove:",
        "ask_format": "Navedi format: online / offline:"
    },
    "sq": {
        "language_text": "👋 Zgjidh gjuhën e botit",
        "main_menu_hint": "👋 Zgjidh një veprim",
        "share_phone_btn": "📱 Ndaj numrin",
        "task": "Kryej detyrën🙏",
        "tutor": "Më duhet një tutor💪",
        "support_btn": "🆘 Mbështetje",
        "menu_btn": "📋 Menu",
        "back": "🏠 Menuja kryesore",
        "one": "Një detyrë",
        "complex": "Ndihmë e plotë për punët",
        "premium_profile": "Profil Premium",
        "choose_service": "👇 Zgjidh një shërbim",
        "my_profile_btn": "👤 Profili im",
        "premium_menu_btn": "⭐ Profil Premium",
        "tutor_login_btn": "🎓 Hyrje tutor",
        "tutor_profile_btn": "📚 Profili i tutorit",
        "tutor_logout_btn": "🚪 Dil nga profili i tutorit",
        "admin_login_btn": "🔐 Hyrje administratori",
        "admin_profile_btn": "🛠 Profili admin",
        "admin_logout_btn": "🚪 Dil nga profili admin",
        "change_language_btn": "🌍 Ndrysho gjuhën",
        "tutor_subject_title": "Zgjidh lëndën për të cilën të duhet tutor:",
        "confirm_btn": "✅ Konfirmo",
        "edit_btn": "✏️ Ndrysho",
        "ask_level": "Shkruaj nivelin ose klasën tënde:",
        "ask_goal": "Përshkruaj shkurt qëllimin ose problemin tënd:",
        "ask_time": "Shkruaj një orar të përshtatshëm për mësimet:",
        "ask_format": "Përcakto formatin: online / offline:"
    },
    "lt": {
        "language_text": "👋 Pasirink boto kalbą",
        "main_menu_hint": "👋 Pasirink veiksmą",
        "share_phone_btn": "📱 Bendrinti numerį",
        "task": "Atlikti užduotį🙏",
        "tutor": "Man reikia korepetitoriaus💪",
        "support_btn": "🆘 Pagalba",
        "menu_btn": "📋 Meniu",
        "back": "🏠 Pagrindinis meniu",
        "one": "Viena užduotis",
        "complex": "Visapusiška pagalba su darbais",
        "premium_profile": "Premium profilis",
        "choose_service": "👇 Pasirink paslaugą",
        "my_profile_btn": "👤 Mano profilis",
        "premium_menu_btn": "⭐ Premium profilis",
        "tutor_login_btn": "🎓 Tutor prisijungimas",
        "tutor_profile_btn": "📚 Tutor profilis",
        "tutor_logout_btn": "🚪 Atsijungti nuo tutor profilio",
        "admin_login_btn": "🔐 Administratoriaus prisijungimas",
        "admin_profile_btn": "🛠 Admin profilis",
        "admin_logout_btn": "🚪 Atsijungti nuo admin profilio",
        "change_language_btn": "🌍 Keisti kalbą",
        "tutor_subject_title": "Pasirink dalyką, kuriam tau reikia korepetitoriaus:",
        "confirm_btn": "✅ Patvirtinti",
        "edit_btn": "✏️ Redaguoti",
        "ask_level": "Nurodyk savo lygį arba klasę:",
        "ask_goal": "Trumpai aprašyk savo tikslą arba problemą:",
        "ask_time": "Nurodyk patogų laiką pamokoms:",
        "ask_format": "Nurodyk formatą: online / offline:"
    },
    "sl": {
        "language_text": "👋 Izberi jezik bota",
        "main_menu_hint": "👋 Izberi dejanje",
        "share_phone_btn": "📱 Deli številko",
        "task": "Opravi nalogo🙏",
        "tutor": "Potrebujem tutorja💪",
        "support_btn": "🆘 Podpora",
        "menu_btn": "📋 Meni",
        "back": "🏠 Glavni meni",
        "one": "Ena naloga",
        "complex": "Celovita pomoč pri nalogah",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Izberi storitev",
        "my_profile_btn": "👤 Moj profil",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Prijava tutorja",
        "tutor_profile_btn": "📚 Tutor profil",
        "tutor_logout_btn": "🚪 Odjava iz tutor profila",
        "admin_login_btn": "🔐 Prijava administratorja",
        "admin_profile_btn": "🛠 Admin profil",
        "admin_logout_btn": "🚪 Odjava iz admin profila",
        "change_language_btn": "🌍 Spremeni jezik",
        "tutor_subject_title": "Izberi predmet, za katerega potrebuješ tutorja:",
        "confirm_btn": "✅ Potrdi",
        "edit_btn": "✏️ Uredi",
        "ask_level": "Vpiši svojo stopnjo ali razred:",
        "ask_goal": "Na kratko opiši svoj cilj ali težavo:",
        "ask_time": "Napiši primeren čas za učne ure:",
        "ask_format": "Navedi obliko: online / offline:"
    },
    "lv": {
        "language_text": "👋 Izvēlies bota valodu",
        "main_menu_hint": "👋 Izvēlies darbību",
        "share_phone_btn": "📱 Kopīgot numuru",
        "task": "Izpildīt uzdevumu🙏",
        "tutor": "Man vajag pasniedzēju💪",
        "support_btn": "🆘 Atbalsts",
        "menu_btn": "📋 Izvēlne",
        "back": "🏠 Galvenā izvēlne",
        "one": "Viens uzdevums",
        "complex": "Pilna palīdzība darbos",
        "premium_profile": "Premium profils",
        "choose_service": "👇 Izvēlies pakalpojumu",
        "my_profile_btn": "👤 Mans profils",
        "premium_menu_btn": "⭐ Premium profils",
        "tutor_login_btn": "🎓 Tutor pieteikšanās",
        "tutor_profile_btn": "📚 Tutor profils",
        "tutor_logout_btn": "🚪 Iziet no tutor profila",
        "admin_login_btn": "🔐 Administratora pieteikšanās",
        "admin_profile_btn": "🛠 Admin profils",
        "admin_logout_btn": "🚪 Iziet no admin profila",
        "change_language_btn": "🌍 Mainīt valodu",
        "tutor_subject_title": "Izvēlies priekšmetu, kuram tev vajag pasniedzēju:",
        "confirm_btn": "✅ Apstiprināt",
        "edit_btn": "✏️ Rediģēt",
        "ask_level": "Norādi savu līmeni vai klasi:",
        "ask_goal": "Īsi apraksti savu mērķi vai problēmu:",
        "ask_time": "Norādi ērtu laiku nodarbībām:",
        "ask_format": "Norādi formātu: online / offline:"
    },
    "et": {
        "language_text": "👋 Vali boti keel",
        "main_menu_hint": "👋 Vali tegevus",
        "share_phone_btn": "📱 Jaga numbrit",
        "task": "Tee ülesanne🙏",
        "tutor": "Mul on vaja juhendajat💪",
        "support_btn": "🆘 Tugi",
        "menu_btn": "📋 Menüü",
        "back": "🏠 Põhimenüü",
        "one": "Üks ülesanne",
        "complex": "Põhjalik abi töödega",
        "premium_profile": "Premium profiil",
        "choose_service": "👇 Vali teenus",
        "my_profile_btn": "👤 Minu profiil",
        "premium_menu_btn": "⭐ Premium profiil",
        "tutor_login_btn": "🎓 Tutor sisselogimine",
        "tutor_profile_btn": "📚 Tutor profiil",
        "tutor_logout_btn": "🚪 Logi tutor-profiilist välja",
        "admin_login_btn": "🔐 Admin sisselogimine",
        "admin_profile_btn": "🛠 Admin profiil",
        "admin_logout_btn": "🚪 Logi admin-profiilist välja",
        "change_language_btn": "🌍 Muuda keelt",
        "tutor_subject_title": "Vali aine, mille jaoks vajad juhendajat:",
        "confirm_btn": "✅ Kinnita",
        "edit_btn": "✏️ Muuda",
        "ask_level": "Sisesta oma tase või klass:",
        "ask_goal": "Kirjelda lühidalt oma eesmärki või probleemi:",
        "ask_time": "Kirjuta sobiv aeg tundideks:",
        "ask_format": "Määra formaat: online / offline:"
    },
    "mk": {
        "language_text": "👋 Избери го јазикот на ботот",
        "main_menu_hint": "👋 Избери акција",
        "share_phone_btn": "📱 Сподели број",
        "task": "Изврши задача🙏",
        "tutor": "Ми треба репетитор💪",
        "support_btn": "🆘 Поддршка",
        "menu_btn": "📋 Мени",
        "back": "🏠 Главно мени",
        "one": "Една задача",
        "complex": "Целосна помош за работи",
        "premium_profile": "Premium профил",
        "choose_service": "👇 Избери услуга",
        "my_profile_btn": "👤 Мој профил",
        "premium_menu_btn": "⭐ Premium профил",
        "tutor_login_btn": "🎓 Влез Tutor",
        "tutor_profile_btn": "📚 Tutor профил",
        "tutor_logout_btn": "🚪 Излез од Tutor профилот",
        "admin_login_btn": "🔐 Влез администратор",
        "admin_profile_btn": "🛠 Admin профил",
        "admin_logout_btn": "🚪 Излез од admin профилот",
        "change_language_btn": "🌍 Смени јазик",
        "tutor_subject_title": "Избери предмет за кој ти треба репетитор:",
        "confirm_btn": "✅ Потврди",
        "edit_btn": "✏️ Уреди",
        "ask_level": "Напиши го твоето ниво или одделение:",
        "ask_goal": "Накратко опиши ја целта или проблемот:",
        "ask_time": "Напиши удобно време за часови:",
        "ask_format": "Наведи формат: онлајн / офлајн:"
    },
    "ka": {
        "language_text": "👋 აირჩიე ბოტის ენა",
        "main_menu_hint": "👋 აირჩიე მოქმედება",
        "share_phone_btn": "📱 ნომრის გაზიარება",
        "task": "დავალების შესრულება🙏",
        "tutor": "რეპეტიტორი მჭირდება💪",
        "support_btn": "🆘 მხარდაჭერა",
        "menu_btn": "📋 მენიუ",
        "back": "🏠 მთავარი მენიუ",
        "one": "ერთი დავალება",
        "complex": "სამუშაოების სრული დახმარება",
        "premium_profile": "Premium პროფილი",
        "choose_service": "👇 აირჩიე სერვისი",
        "my_profile_btn": "👤 ჩემი პროფილი",
        "premium_menu_btn": "⭐ Premium პროფილი",
        "tutor_login_btn": "🎓 Tutor შესვლა",
        "tutor_profile_btn": "📚 Tutor პროფილი",
        "tutor_logout_btn": "🚪 Tutor პროფილიდან გასვლა",
        "admin_login_btn": "🔐 ადმინისტრატორის შესვლა",
        "admin_profile_btn": "🛠 Admin პროფილი",
        "admin_logout_btn": "🚪 Admin პროფილიდან გასვლა",
        "change_language_btn": "🌍 ენის შეცვლა",
        "tutor_subject_title": "აირჩიე საგანი, რომელშიც რეპეტიტორი გჭირდება:",
        "confirm_btn": "✅ დადასტურება",
        "edit_btn": "✏️ რედაქტირება",
        "ask_level": "მიუთითე შენი დონე ან კლასი:",
        "ask_goal": "მოკლედ აღწერე შენი მიზანი ან პრობლემა:",
        "ask_time": "ჩაწერე მოსახერხებელი დრო გაკვეთილებისთვის:",
        "ask_format": "მიუთითე ფორმატი: ონლაინ / ოფლაინ:"
    },
    "hy": {
        "language_text": "👋 Ընտրիր բոտի լեզուն",
        "main_menu_hint": "👋 Ընտրիր գործողություն",
        "share_phone_btn": "📱 Կիսվել համարով",
        "task": "Կատարել առաջադրանքը🙏",
        "tutor": "Ինձ պետք է դասախոս💪",
        "support_btn": "🆘 Աջակցություն",
        "menu_btn": "📋 Մենյու",
        "back": "🏠 Գլխավոր մենյու",
        "one": "Մեկ առաջադրանք",
        "complex": "Լիարժեք օգնություն աշխատանքների համար",
        "premium_profile": "Premium պրոֆիլ",
        "choose_service": "👇 Ընտրիր ծառայություն",
        "my_profile_btn": "👤 Իմ պրոֆիլը",
        "premium_menu_btn": "⭐ Premium պրոֆիլ",
        "tutor_login_btn": "🎓 Tutor մուտք",
        "tutor_profile_btn": "📚 Tutor պրոֆիլ",
        "tutor_logout_btn": "🚪 Դուրս գալ tutor պրոֆիլից",
        "admin_login_btn": "🔐 Ադմինի մուտք",
        "admin_profile_btn": "🛠 Admin պրոֆիլ",
        "admin_logout_btn": "🚪 Դուրս գալ admin պրոֆիլից",
        "change_language_btn": "🌍 Փոխել լեզուն",
        "tutor_subject_title": "Ընտրիր առարկան, որի համար քեզ պետք է tutor:",
        "confirm_btn": "✅ Հաստատել",
        "edit_btn": "✏️ Խմբագրել",
        "ask_level": "Նշիր քո մակարդակը կամ դասարանը:",
        "ask_goal": "Կարճ նկարագրիր քո նպատակը կամ խնդիրը:",
        "ask_time": "Գրիր հարմար ժամանակ դասերի համար:",
        "ask_format": "Նշիր ձևաչափը՝ online / offline:"
    },
    "az": {
        "language_text": "👋 Botun dilini seç",
        "main_menu_hint": "👋 Əməliyyat seç",
        "share_phone_btn": "📱 Nömrəni paylaş",
        "task": "Tapşırığı yerinə yetir🙏",
        "tutor": "Mənə repetitor lazımdır💪",
        "support_btn": "🆘 Dəstək",
        "menu_btn": "📋 Menyu",
        "back": "🏠 Əsas menyu",
        "one": "Bir tapşırıq",
        "complex": "İşlər üçün tam yardım",
        "premium_profile": "Premium profil",
        "choose_service": "👇 Xidməti seç",
        "my_profile_btn": "👤 Profilim",
        "premium_menu_btn": "⭐ Premium profil",
        "tutor_login_btn": "🎓 Tutor girişi",
        "tutor_profile_btn": "📚 Tutor profili",
        "tutor_logout_btn": "🚪 Tutor profilindən çıx",
        "admin_login_btn": "🔐 Administrator girişi",
        "admin_profile_btn": "🛠 Admin profili",
        "admin_logout_btn": "🚪 Admin profilindən çıx",
        "change_language_btn": "🌍 Dili dəyiş",
        "tutor_subject_title": "Repetitor lazım olan fənni seç:",
        "confirm_btn": "✅ Təsdiqlə",
        "edit_btn": "✏️ Redaktə et",
        "ask_level": "Səviyyəni və ya sinfini yaz:",
        "ask_goal": "Məqsədini və ya problemini qısa yaz:",
        "ask_time": "Dərslər üçün uyğun vaxtı yaz:",
        "ask_format": "Formatı göstər: onlayn / oflayn:"
    },
    "ca": {
        "language_text": "👋 Tria l’idioma del bot",
        "main_menu_hint": "👋 Tria una acció",
        "share_phone_btn": "📱 Comparteix el número",
        "task": "Fer una tasca🙏",
        "tutor": "Necessito un tutor💪",
        "support_btn": "🆘 Suport",
        "menu_btn": "📋 Menú",
        "back": "🏠 Menú principal",
        "one": "Una tasca",
        "complex": "Ajuda completa amb treballs",
        "premium_profile": "Perfil Premium",
        "choose_service": "👇 Tria un servei",
        "my_profile_btn": "👤 El meu perfil",
        "premium_menu_btn": "⭐ Perfil Premium",
        "tutor_login_btn": "🎓 Inici de sessió tutor",
        "tutor_profile_btn": "📚 Perfil tutor",
        "tutor_logout_btn": "🚪 Sortir del perfil tutor",
        "admin_login_btn": "🔐 Inici de sessió administrador",
        "admin_profile_btn": "🛠 Perfil admin",
        "admin_logout_btn": "🚪 Sortir del perfil admin",
        "change_language_btn": "🌍 Canvia la llengua",
        "tutor_subject_title": "Tria l’assignatura per a la qual necessites un tutor:",
        "confirm_btn": "✅ Confirma",
        "edit_btn": "✏️ Edita",
        "ask_level": "Indica el teu nivell o curs:",
        "ask_goal": "Descriu breument el teu objectiu o problema:",
        "ask_time": "Indica un horari còmode per a les classes:",
        "ask_format": "Indica el format: en línia / presencial:"
    },
    "is": {
        "language_text": "👋 Veldu tungumál botsins",
        "main_menu_hint": "👋 Veldu aðgerð",
        "share_phone_btn": "📱 Deila númeri",
        "task": "Leysa verkefni🙏",
        "tutor": "Ég þarf leiðbeinanda💪",
        "support_btn": "🆘 Stuðningur",
        "menu_btn": "📋 Valmynd",
        "back": "🏠 Aðalvalmynd",
        "one": "Eitt verkefni",
        "complex": "Heildarhjálp með verkefni",
        "premium_profile": "Premium prófíll",
        "choose_service": "👇 Veldu þjónustu",
        "my_profile_btn": "👤 Minn prófíll",
        "premium_menu_btn": "⭐ Premium prófíll",
        "tutor_login_btn": "🎓 Tutor innskráning",
        "tutor_profile_btn": "📚 Tutor prófíll",
        "tutor_logout_btn": "🚪 Skrá út úr tutor prófíl",
        "admin_login_btn": "🔐 Innskráning stjórnanda",
        "admin_profile_btn": "🛠 Admin prófíll",
        "admin_logout_btn": "🚪 Skrá út úr admin prófíl",
        "change_language_btn": "🌍 Breyta tungumáli",
        "tutor_subject_title": "Veldu fagið sem þú þarft tutor fyrir:",
        "confirm_btn": "✅ Staðfesta",
        "edit_btn": "✏️ Breyta",
        "ask_level": "Skrifaðu stig eða bekk:",
        "ask_goal": "Lýstu markmiði þínu eða vandamáli stuttlega:",
        "ask_time": "Skrifaðu hentugan tíma fyrir kennsluna:",
        "ask_format": "Tilgreindu snið: online / offline:"
    },
    "ga": {
        "language_text": "👋 Roghnaigh teanga an bhot",
        "main_menu_hint": "👋 Roghnaigh gníomh",
        "share_phone_btn": "📱 Comhroinn uimhir",
        "task": "Déan tasc🙏",
        "tutor": "Teastaíonn teagascóir uaim💪",
        "support_btn": "🆘 Tacaíocht",
        "menu_btn": "📋 Roghchlár",
        "back": "🏠 Príomhroghchlár",
        "one": "Tasc amháin",
        "complex": "Cabhair iomlán le hobair",
        "premium_profile": "Próifíl Premium",
        "choose_service": "👇 Roghnaigh seirbhís",
        "my_profile_btn": "👤 Mo phróifíl",
        "premium_menu_btn": "⭐ Próifíl Premium",
        "tutor_login_btn": "🎓 Logáil isteach tutor",
        "tutor_profile_btn": "📚 Próifíl tutor",
        "tutor_logout_btn": "🚪 Logáil amach as próifíl tutor",
        "admin_login_btn": "🔐 Logáil isteach riarthóra",
        "admin_profile_btn": "🛠 Próifíl admin",
        "admin_logout_btn": "🚪 Logáil amach as próifíl admin",
        "change_language_btn": "🌍 Athraigh teanga",
        "tutor_subject_title": "Roghnaigh an t-ábhar a bhfuil tutor uait dó:",
        "confirm_btn": "✅ Deimhnigh",
        "edit_btn": "✏️ Cuir in eagar",
        "ask_level": "Cuir isteach do leibhéal nó do rang:",
        "ask_goal": "Déan cur síos gairid ar do sprioc nó fadhb:",
        "ask_time": "Scríobh am áisiúil do na ceachtanna:",
        "ask_format": "Sonraigh an fhormáid: ar líne / as líne:"
    },
    "mt": {
        "language_text": "👋 Agħżel il-lingwa tal-bot",
        "main_menu_hint": "👋 Agħżel azzjoni",
        "share_phone_btn": "📱 Aqsam in-numru",
        "task": "Agħmel kompitu🙏",
        "tutor": "Għandi bżonn tutor💪",
        "support_btn": "🆘 Appoġġ",
        "menu_btn": "📋 Menu",
        "back": "🏠 Menu prinċipali",
        "one": "Kompitu wieħed",
        "complex": "Għajnuna sħiħa għax-xogħol",
        "premium_profile": "Profil Premium",
        "choose_service": "👇 Agħżel servizz",
        "my_profile_btn": "👤 Il-profil tiegħi",
        "premium_menu_btn": "⭐ Profil Premium",
        "tutor_login_btn": "🎓 Tutor login",
        "tutor_profile_btn": "📚 Profil tutor",
        "tutor_logout_btn": "🚪 Oħroġ mill-profil tutor",
        "admin_login_btn": "🔐 Login tal-amministratur",
        "admin_profile_btn": "🛠 Profil admin",
        "admin_logout_btn": "🚪 Oħroġ mill-profil admin",
        "change_language_btn": "🌍 Ibdel il-lingwa",
        "tutor_subject_title": "Agħżel is-suġġett li għalih għandek bżonn tutor:",
        "confirm_btn": "✅ Ikkonferma",
        "edit_btn": "✏️ Editja",
        "ask_level": "Ikteb il-livell jew il-klassi tiegħek:",
        "ask_goal": "Iddeskrivi fil-qosor il-mira jew il-problema tiegħek:",
        "ask_time": "Ikteb ħin konvenjenti għall-lezzjonijiet:",
        "ask_format": "Speċifika l-format: online / offline:"
    },
    "lb": {
        "language_text": "👋 Wielt d'Sprooch vum Bot",
        "main_menu_hint": "👋 Wielt eng Aktioun",
        "share_phone_btn": "📱 Nummer deelen",
        "task": "Aufgab maachen🙏",
        "tutor": "Ech brauch en Tutor💪",
        "support_btn": "🆘 Support",
        "menu_btn": "📋 Menü",
        "back": "🏠 Haaptmenü",
        "one": "Eng Aufgab",
        "complex": "Komplett Hëllef bei Aarbechten",
        "premium_profile": "Premium-Profil",
        "choose_service": "👇 Wielt e Service",
        "my_profile_btn": "👤 Mäi Profil",
        "premium_menu_btn": "⭐ Premium-Profil",
        "tutor_login_btn": "🎓 Tutor-Login",
        "tutor_profile_btn": "📚 Tutor-Profil",
        "tutor_logout_btn": "🚪 Aus dem Tutor-Profil ausloggen",
        "admin_login_btn": "🔐 Admin-Login",
        "admin_profile_btn": "🛠 Admin-Profil",
        "admin_logout_btn": "🚪 Aus dem Admin-Profil ausloggen",
        "change_language_btn": "🌍 Sprooch änneren",
        "tutor_subject_title": "Wielt d'Fach, fir dats du en Tutor brauchs:",
        "confirm_btn": "✅ Bestätegen",
        "edit_btn": "✏️ Änneren",
        "ask_level": "Gëff däin Niveau oder deng Klass un:",
        "ask_goal": "Beschreif kuerz däin Zil oder Problem:",
        "ask_time": "Schreif eng passend Zäit fir d'Coursen:",
        "ask_format": "Gëff de Format un: online / offline:"
    }
}

SUBJECT_ORDER = [
    "mathematics",
    "english",
    "native_language",
    "physics",
    "chemistry",
    "biology",
    "computer_science",
    "programming",
    "history",
    "geography",
    "economics",
    "accounting",
    "german",
    "french",
    "music",
    "art"
]

SUBJECT_TRANSLATIONS_RAW = {
    "ua": [
        "Математика",
        "Англійська мова",
        "Рідна мова та література",
        "Фізика",
        "Хімія",
        "Біологія",
        "Інформатика",
        "Програмування",
        "Історія",
        "Географія",
        "Економіка",
        "Бухгалтерський облік",
        "Німецька мова",
        "Французька мова",
        "Музика",
        "Мистецтво"
    ],
    "ru": [
        "Математика",
        "Английский язык",
        "Родной язык и литература",
        "Физика",
        "Химия",
        "Биология",
        "Информатика",
        "Программирование",
        "История",
        "География",
        "Экономика",
        "Бухгалтерский учет",
        "Немецкий язык",
        "Французский язык",
        "Музыка",
        "Искусство"
    ],
    "en": [
        "Mathematics",
        "English language",
        "Native language and literature",
        "Physics",
        "Chemistry",
        "Biology",
        "Computer science",
        "Programming",
        "History",
        "Geography",
        "Economics",
        "Accounting",
        "German language",
        "French language",
        "Music",
        "Art"
    ],
    "es": [
        "Matemáticas",
        "Inglés",
        "Lengua y literatura",
        "Física",
        "Química",
        "Biología",
        "Informática",
        "Programación",
        "Historia",
        "Geografía",
        "Economía",
        "Contabilidad",
        "Alemán",
        "Francés",
        "Música",
        "Arte"
    ],
    "de": [
        "Mathematik",
        "Englisch",
        "Muttersprache und Literatur",
        "Physik",
        "Chemie",
        "Biologie",
        "Informatik",
        "Programmierung",
        "Geschichte",
        "Geografie",
        "Wirtschaft",
        "Buchhaltung",
        "Deutsch",
        "Französisch",
        "Musik",
        "Kunst"
    ],
    "fr": [
        "Mathématiques",
        "Anglais",
        "Langue et littérature",
        "Physique",
        "Chimie",
        "Biologie",
        "Informatique",
        "Programmation",
        "Histoire",
        "Géographie",
        "Économie",
        "Comptabilité",
        "Allemand",
        "Français",
        "Musique",
        "Art"
    ],
    "it": [
        "Matematica",
        "Inglese",
        "Lingua e letteratura",
        "Fisica",
        "Chimica",
        "Biologia",
        "Informatica",
        "Programmazione",
        "Storia",
        "Geografia",
        "Economia",
        "Contabilità",
        "Tedesco",
        "Francese",
        "Musica",
        "Arte"
    ],
    "tr": [
        "Matematik",
        "İngilizce",
        "Ana dil ve edebiyat",
        "Fizik",
        "Kimya",
        "Biyoloji",
        "Bilgisayar bilimi",
        "Programlama",
        "Tarih",
        "Coğrafya",
        "Ekonomi",
        "Muhasebe",
        "Almanca",
        "Fransızca",
        "Müzik",
        "Sanat"
    ],
    "pl": [
        "Matematyka",
        "Język angielski",
        "Język ojczysty i literatura",
        "Fizyka",
        "Chemia",
        "Biologia",
        "Informatyka",
        "Programowanie",
        "Historia",
        "Geografia",
        "Ekonomia",
        "Rachunkowość",
        "Język niemiecki",
        "Język francuski",
        "Muzyka",
        "Sztuka"
    ],
    "ro": [
        "Matematică",
        "Limba engleză",
        "Limba și literatura",
        "Fizică",
        "Chimie",
        "Biologie",
        "Informatică",
        "Programare",
        "Istorie",
        "Geografie",
        "Economie",
        "Contabilitate",
        "Limba germană",
        "Limba franceză",
        "Muzică",
        "Artă"
    ],
    "nl": [
        "Wiskunde",
        "Engels",
        "Taal en literatuur",
        "Natuurkunde",
        "Scheikunde",
        "Biologie",
        "Informatica",
        "Programmeren",
        "Geschiedenis",
        "Aardrijkskunde",
        "Economie",
        "Boekhouding",
        "Duits",
        "Frans",
        "Muziek",
        "Kunst"
    ],
    "el": [
        "Μαθηματικά",
        "Αγγλικά",
        "Γλώσσα και λογοτεχνία",
        "Φυσική",
        "Χημεία",
        "Βιολογία",
        "Πληροφορική",
        "Προγραμματισμός",
        "Ιστορία",
        "Γεωγραφία",
        "Οικονομικά",
        "Λογιστική",
        "Γερμανικά",
        "Γαλλικά",
        "Μουσική",
        "Τέχνη"
    ],
    "cs": [
        "Matematika",
        "Angličtina",
        "Rodný jazyk a literatura",
        "Fyzika",
        "Chemie",
        "Biologie",
        "Informatika",
        "Programování",
        "Dějepis",
        "Zeměpis",
        "Ekonomie",
        "Účetnictví",
        "Němčina",
        "Francouzština",
        "Hudba",
        "Umění"
    ],
    "pt": [
        "Matemática",
        "Inglês",
        "Língua e literatura",
        "Física",
        "Química",
        "Biologia",
        "Informática",
        "Programação",
        "História",
        "Geografia",
        "Economia",
        "Contabilidade",
        "Alemão",
        "Francês",
        "Música",
        "Arte"
    ],
    "sv": [
        "Matematik",
        "Engelska",
        "Modersmål och litteratur",
        "Fysik",
        "Kemi",
        "Biologi",
        "Datavetenskap",
        "Programmering",
        "Historia",
        "Geografi",
        "Ekonomi",
        "Bokföring",
        "Tyska",
        "Franska",
        "Musik",
        "Konst"
    ],
    "hu": [
        "Matematika",
        "Angol nyelv",
        "Anyanyelv és irodalom",
        "Fizika",
        "Kémia",
        "Biológia",
        "Informatika",
        "Programozás",
        "Történelem",
        "Földrajz",
        "Közgazdaságtan",
        "Könyvelés",
        "Német nyelv",
        "Francia nyelv",
        "Zene",
        "Művészet"
    ],
    "be": [
        "Матэматыка",
        "Англійская мова",
        "Родная мова і літаратура",
        "Фізіка",
        "Хімія",
        "Біялогія",
        "Інфарматыка",
        "Праграмаванне",
        "Гісторыя",
        "Геаграфія",
        "Эканоміка",
        "Бухгалтарскі ўлік",
        "Нямецкая мова",
        "Французская мова",
        "Музыка",
        "Мастацтва"
    ],
    "bg": [
        "Математика",
        "Английски език",
        "Роден език и литература",
        "Физика",
        "Химия",
        "Биология",
        "Информатика",
        "Програмиране",
        "История",
        "География",
        "Икономика",
        "Счетоводство",
        "Немски език",
        "Френски език",
        "Музика",
        "Изкуство"
    ],
    "sr": [
        "Matematika",
        "Engleski jezik",
        "Maternji jezik i književnost",
        "Fizika",
        "Hemija",
        "Biologija",
        "Informatika",
        "Programiranje",
        "Istorija",
        "Geografija",
        "Ekonomija",
        "Računovodstvo",
        "Nemački jezik",
        "Francuski jezik",
        "Muzika",
        "Umetnost"
    ],
    "da": [
        "Matematik",
        "Engelsk",
        "Modersmål og litteratur",
        "Fysik",
        "Kemi",
        "Biologi",
        "Datalogi",
        "Programmering",
        "Historie",
        "Geografi",
        "Økonomi",
        "Regnskab",
        "Tysk",
        "Fransk",
        "Musik",
        "Kunst"
    ],
    "fi": [
        "Matematiikka",
        "Englanti",
        "Äidinkieli ja kirjallisuus",
        "Fysiikka",
        "Kemia",
        "Biologia",
        "Tietojenkäsittely",
        "Ohjelmointi",
        "Historia",
        "Maantiede",
        "Talous",
        "Kirjanpito",
        "Saksa",
        "Ranska",
        "Musiikki",
        "Taide"
    ],
    "sk": [
        "Matematika",
        "Angličtina",
        "Materinský jazyk a literatúra",
        "Fyzika",
        "Chémia",
        "Biológia",
        "Informatika",
        "Programovanie",
        "História",
        "Geografia",
        "Ekonómia",
        "Účtovníctvo",
        "Nemčina",
        "Francúzština",
        "Hudba",
        "Umenie"
    ],
    "no": [
        "Matematikk",
        "Engelsk",
        "Morsmål og litteratur",
        "Fysikk",
        "Kjemi",
        "Biologi",
        "Informatikk",
        "Programmering",
        "Historie",
        "Geografi",
        "Økonomi",
        "Regnskap",
        "Tysk",
        "Fransk",
        "Musikk",
        "Kunst"
    ],
    "hr": [
        "Matematika",
        "Engleski jezik",
        "Materinji jezik i književnost",
        "Fizika",
        "Kemija",
        "Biologija",
        "Informatika",
        "Programiranje",
        "Povijest",
        "Geografija",
        "Ekonomija",
        "Računovodstvo",
        "Njemački jezik",
        "Francuski jezik",
        "Glazba",
        "Umjetnost"
    ],
    "bs": [
        "Matematika",
        "Engleski jezik",
        "Maternji jezik i književnost",
        "Fizika",
        "Hemija",
        "Biologija",
        "Informatika",
        "Programiranje",
        "Historija",
        "Geografija",
        "Ekonomija",
        "Računovodstvo",
        "Njemački jezik",
        "Francuski jezik",
        "Muzika",
        "Umjetnost"
    ],
    "sq": [
        "Matematikë",
        "Anglisht",
        "Gjuha amtare dhe letërsia",
        "Fizikë",
        "Kimi",
        "Biologji",
        "Informatikë",
        "Programim",
        "Histori",
        "Gjeografi",
        "Ekonomi",
        "Kontabilitet",
        "Gjermanisht",
        "Frëngjisht",
        "Muzikë",
        "Art"
    ],
    "lt": [
        "Matematika",
        "Anglų kalba",
        "Gimtoji kalba ir literatūra",
        "Fizika",
        "Chemija",
        "Biologija",
        "Informatika",
        "Programavimas",
        "Istorija",
        "Geografija",
        "Ekonomika",
        "Apskaita",
        "Vokiečių kalba",
        "Prancūzų kalba",
        "Muzika",
        "Menas"
    ],
    "sl": [
        "Matematika",
        "Angleščina",
        "Materni jezik in književnost",
        "Fizika",
        "Kemija",
        "Biologija",
        "Računalništvo",
        "Programiranje",
        "Zgodovina",
        "Geografija",
        "Ekonomija",
        "Računovodstvo",
        "Nemščina",
        "Francoščina",
        "Glasba",
        "Umetnost"
    ],
    "lv": [
        "Matemātika",
        "Angļu valoda",
        "Dzimtā valoda un literatūra",
        "Fizika",
        "Ķīmija",
        "Bioloģija",
        "Informātika",
        "Programmēšana",
        "Vēsture",
        "Ģeogrāfija",
        "Ekonomika",
        "Grāmatvedība",
        "Vācu valoda",
        "Franču valoda",
        "Mūzika",
        "Māksla"
    ],
    "et": [
        "Matemaatika",
        "Inglise keel",
        "Emakeel ja kirjandus",
        "Füüsika",
        "Keemia",
        "Bioloogia",
        "Informaatika",
        "Programmeerimine",
        "Ajalugu",
        "Geograafia",
        "Majandus",
        "Raamatupidamine",
        "Saksa keel",
        "Prantsuse keel",
        "Muusika",
        "Kunst"
    ],
    "mk": [
        "Математика",
        "Англиски јазик",
        "Мајчин јазик и литература",
        "Физика",
        "Хемија",
        "Биологија",
        "Информатика",
        "Програмирање",
        "Историја",
        "Географија",
        "Економија",
        "Сметководство",
        "Германски јазик",
        "Француски јазик",
        "Музика",
        "Уметност"
    ],
    "ka": [
        "მათემატიკა",
        "ინგლისური ენა",
        "მშობლიური ენა და ლიტერატურა",
        "ფიზიკა",
        "ქიმია",
        "ბიოლოგია",
        "ინფორმატიკა",
        "პროგრამირება",
        "ისტორია",
        "გეოგრაფია",
        "ეკონომიკა",
        "ბუღალტერია",
        "გერმანული ენა",
        "ფრანგული ენა",
        "მუსიკა",
        "ხელოვნება"
    ],
    "hy": [
        "Մաթեմատիկա",
        "Անգլերեն",
        "Մայրենի լեզու և գրականություն",
        "Ֆիզիկա",
        "Քիմիա",
        "Կենսաբանություն",
        "Ինֆորմատիկա",
        "Ծրագրավորում",
        "Պատմություն",
        "Աշխարհագրություն",
        "Տնտեսագիտություն",
        "Հաշվապահություն",
        "Գերմաներեն",
        "Ֆրանսերեն",
        "Երաժշտություն",
        "Արվեստ"
    ],
    "az": [
        "Riyaziyyat",
        "İngilis dili",
        "Ana dili və ədəbiyyat",
        "Fizika",
        "Kimya",
        "Biologiya",
        "İnformatika",
        "Proqramlaşdırma",
        "Tarix",
        "Coğrafiya",
        "İqtisadiyyat",
        "Mühasibat uçotu",
        "Alman dili",
        "Fransız dili",
        "Musiqi",
        "İncəsənət"
    ],
    "ca": [
        "Matemàtiques",
        "Anglès",
        "Llengua i literatura",
        "Física",
        "Química",
        "Biologia",
        "Informàtica",
        "Programació",
        "Història",
        "Geografia",
        "Economia",
        "Comptabilitat",
        "Alemany",
        "Francès",
        "Música",
        "Art"
    ],
    "is": [
        "Stærðfræði",
        "Enska",
        "Móðurmál og bókmenntir",
        "Eðlisfræði",
        "Efnafræði",
        "Líffræði",
        "Tölvunarfræði",
        "Forritun",
        "Saga",
        "Landafræði",
        "Hagfræði",
        "Bókhald",
        "Þýska",
        "Franska",
        "Tónlist",
        "List"
    ],
    "ga": [
        "Matamaitic",
        "Béarla",
        "Teanga dhúchais agus litríocht",
        "Fisic",
        "Ceimic",
        "Bitheolaíocht",
        "Ríomheolaíocht",
        "Cláirú",
        "Stair",
        "Tíreolaíocht",
        "Eacnamaíocht",
        "Cuntasaíocht",
        "Gearmáinis",
        "Fraincis",
        "Ceol",
        "Ealaín"
    ],
    "mt": [
        "Matematika",
        "Ingliż",
        "Lingwa u letteratura",
        "Fiżika",
        "Kimika",
        "Bijoloġija",
        "Informatika",
        "Programmar",
        "Storja",
        "Ġeografija",
        "Ekonomija",
        "Kontabilità",
        "Ġermaniż",
        "Franċiż",
        "Mużika",
        "Arti"
    ],
    "lb": [
        "Mathematik",
        "Englesch",
        "Mammesprooch a Literatur",
        "Physik",
        "Chimie",
        "Biologie",
        "Informatik",
        "Programméieren",
        "Geschicht",
        "Geografie",
        "Ekonomie",
        "Comptabilitéit",
        "Däitsch",
        "Franséisch",
        "Musek",
        "Konscht"
    ]
}

SUBJECT_TRANSLATIONS = {
    subject_id: {
        lang_code: SUBJECT_TRANSLATIONS_RAW[lang_code][index]
        for lang_code in SUBJECT_TRANSLATIONS_RAW
    }
    for index, subject_id in enumerate(SUBJECT_ORDER)
}

SUBJECT_LABEL_TO_ID = {}
for subject_id in SUBJECT_ORDER:
    for lang_code, label in SUBJECT_TRANSLATIONS[subject_id].items():
        SUBJECT_LABEL_TO_ID[label] = subject_id


def build_texts():
    texts = {}
    texts["en"] = dict(BASE_TEXTS_EN)
    texts["ua"] = {**BASE_TEXTS_EN, **BASE_TEXTS_UA}
    texts["ru"] = {**BASE_TEXTS_EN, **BASE_TEXTS_RU}

    for code, _, _ in LANGUAGE_DEFINITIONS:
        if code in texts:
            continue
        texts[code] = {**BASE_TEXTS_EN, **LANGUAGE_MENU_OVERRIDES.get(code, {})}

    return texts


TEXTS = build_texts()


def get_subject_name(lang: str, subject_id: str) -> str:
    if subject_id not in SUBJECT_TRANSLATIONS:
        return subject_id
    names = SUBJECT_TRANSLATIONS[subject_id]
    return names.get(lang) or names.get("en") or subject_id


def resolve_subject_id(value: str | None) -> str:
    if not value:
        return ""
    if value in SUBJECT_TRANSLATIONS:
        return value
    return SUBJECT_LABEL_TO_ID.get(value, value)


def localize_subject_value(value: str | None, lang: str) -> str:
    if not value:
        return "-"
    subject_id = resolve_subject_id(value)
    if subject_id in SUBJECT_TRANSLATIONS:
        return get_subject_name(lang, subject_id)
    return value


PAYMENT_TYPE_ALIASES = {
    "task": "task",
    "complex": "complex",
    "premium_profile": "premium_profile",
    "Одне завдання": "task",
    "Одно задание": "task",
    "One task": "task",
    "Комплексне виконання роботи": "complex",
    "Комплексное выполнение работы": "complex",
    "Comprehensive assignment help": "complex",
    "Преміум профіль": "premium_profile",
    "Премиум профиль": "premium_profile",
    "Premium Profile": "premium_profile",
    "Premium profile": "premium_profile"
}


def normalize_payment_type(value: str | None) -> str:
    if not value:
        return ""
    return PAYMENT_TYPE_ALIASES.get(value, value)


def get_payment_type_label(value: str | None, lang: str) -> str:
    payment_code = normalize_payment_type(value)
    if payment_code == "task":
        return TEXTS[lang]["one"]
    if payment_code == "complex":
        return TEXTS[lang]["complex"]
    if payment_code == "premium_profile":
        return TEXTS[lang]["premium_profile"]
    return value or "-"


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
    balance, target, _ = get_tutor_withdraw_progress(tutor_user_id)
    return f"{TEXTS[lang]['tutor_withdraw_btn']} {balance}/{target}⭐"


def is_tutor_withdraw_button_text(text_value: str, tutor_user_id: int, lang: str) -> bool:
    return text_value == TEXTS[lang]['tutor_withdraw_btn'] or text_value == get_tutor_withdraw_button_text(tutor_user_id, lang)


def build_tutor_balance_info_text(tutor_user_id: int, lang: str) -> str:
    balance, _target, remaining = get_tutor_withdraw_progress(tutor_user_id)
    if remaining > 0:
        return (
            f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\n"
            f"{TEXTS[lang]['withdraw_left_to_earn'].format(remaining=remaining)}"
        )
    return (
        f"{TEXTS[lang]['tutor_balance_label']}: {balance}⭐\n"
        f"{TEXTS[lang]['withdraw_available_now']}"
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
    if not language_code:
        return "ua"

    code = language_code.lower().replace("_", "-").strip()
    for candidate in (code, code.split("-")[0]):
        if candidate in TELEGRAM_LANGUAGE_ALIASES:
            return TELEGRAM_LANGUAGE_ALIASES[candidate]

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
            lines.append(f"• {get_payment_type_label(payment_type, lang)} — {amount_stars}⭐ ({created_at[:16]})")
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
        payment_part = f"{get_payment_type_label(request_data.get('payment_type'), lang)} | {request_data.get('payment_amount_stars')}⭐"

    subject_text = localize_subject_value(request_data.get("subject"), lang)

    return (
        f"{TEXTS[lang]['tutor_request_detail_title']} #{request_data['id']}\n\n"
        f"{TEXTS[lang]['complaint_user_id']}: {request_data['user_id']}\n"
        f"{TEXTS[lang]['tutor_subject']}: {subject_text}\n"
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
    kb.row(KeyboardButton(TEXTS[lang]["share_phone_btn"], request_contact=True))
    kb.row(TEXTS[lang]["back"])
    return kb


def system_menu(lang: str = "ua", is_admin: bool = False, is_tutor: bool = False):
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

    if not is_admin and not is_tutor:
        kb.row(TEXTS[lang]["premium_menu_btn"])

    kb.row(TEXTS[lang]["my_profile_btn"])
    kb.row(TEXTS[lang]["back"])
    return kb


def premium_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
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


def tutor_menu(user_id: int, lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["tutor_new_requests_btn"])
    kb.row(TEXTS[lang]["tutor_my_requests_btn"])
    kb.row(get_tutor_withdraw_button_text(user_id, lang))
    kb.row(TEXTS[lang]["back"])
    return kb


def get_language_keyboard(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for button_text in LANG_BUTTONS.keys():
        row.append(button_text)
        if len(row) == 2:
            kb.row(*row)
            row = []

    if row:
        kb.row(*row)

    kb.row(TEXTS[lang]["back"])
    return kb


def get_task_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["one"])
    kb.row(TEXTS[lang]["complex"])
    kb.row(TEXTS[lang]["premium_profile"])
    kb.row(TEXTS[lang]["back"])
    return kb


def get_tutor_subject_buttons(lang: str) -> dict[str, str]:
    return {get_subject_name(lang, subject_id): subject_id for subject_id in SUBJECT_ORDER}


def get_tutor_subjects_menu(lang: str = "ua"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    subjects_map = get_tutor_subject_buttons(lang)
    row = []

    for subject_button in subjects_map.keys():
        row.append(subject_button)
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
        subject = localize_subject_value(row[3], lang)
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
    ensure_user(message.from_user.id)
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)

    user_state[message.from_user.id] = "start_phone_wait"
    await message.answer(TEXTS[lang]["start_phone_request"], reply_markup=get_start_phone_menu(lang))


@dp.message_handler(commands=["myprofile"])
async def cmd_myprofile(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "profile_screen"
    await message.answer(build_profile_text(message.from_user.id, lang), reply_markup=profile_menu(lang))


@dp.message_handler(commands=["premium"])
async def cmd_premium(message: types.Message):
    sync_user_telegram_name(message.from_user)
    lang = resolve_user_language(message)
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
            f"{TEXTS[lang]['new_order_prefix']}: {get_payment_type_label(pending_payment, lang)}",
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
        user_state[message.from_user.id] = "profile_screen"
        await message.answer(build_profile_text(message.from_user.id, lang), reply_markup=profile_menu(lang))
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
        user_state[message.from_user.id] = "tutor_subject_wait"
        await message.answer(TEXTS[lang]["tutor_subject_title"], reply_markup=get_tutor_subjects_menu(lang))
        return

    if state == "tutor_subject_wait":
        subject_buttons = get_tutor_subject_buttons(lang)

        if text not in subject_buttons:
            await message.answer(
                TEXTS[lang]["choose_valid_subject"],
                reply_markup=get_tutor_subjects_menu(lang)
            )
            return

        user_temp.setdefault(message.from_user.id, {})
        user_temp[message.from_user.id]["subject"] = subject_buttons[text]
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
            f"{TEXTS[lang]['tutor_subject']}: {localize_subject_value(d.get('subject'), lang)}\n"
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
            category="",
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
            f"{TEXTS[lang]['tutor_subject']}: {localize_subject_value(d.get('subject'), lang)}",
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
                payment_info = f"{get_payment_type_label(payment_type, lang)} | {payment_amount}⭐"

            request_text = (
                f"{TEXTS[lang]['tutor_request_detail_title']} #{request_id}\n\n"
                f"{TEXTS[lang]['complaint_user_id']}: {user_id}\n"
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
        BotCommand("myprofile", "My profile"),
        BotCommand("premium", "Premium profile"),
        BotCommand("complaint", "Support"),
        BotCommand("language", "Change language"),
        BotCommand("admin", "Admin login"),
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
