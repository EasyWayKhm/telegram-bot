import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, BotCommand
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
user_lang_manual = {}

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
        "profile_text": "🧾 Розділ «Моя анкета» в розробці.",
        "premium_text": "💎 Розділ Premium в розробці.",
        "complain_text": "⚠️ Напиши свою скаргу одним повідомленням, і адміністратор її побачить.",
        "complaint_sent": "✅ Скаргу відправлено адміністратору.",
        "send_file_now": "📎 Тепер можеш надіслати файл.",
        "premium_profile_activated": "💎 Преміум профіль активовано.",
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
        "profile_text": "🧾 Раздел «Моя анкета» в разработке.",
        "premium_text": "💎 Раздел Premium в разработке.",
        "complain_text": "⚠️ Напишите вашу жалобу одним сообщением, и администратор её увидит.",
        "complaint_sent": "✅ Жалоба отправлена администратору.",
        "send_file_now": "📎 Теперь можете отправить файл.",
        "premium_profile_activated": "💎 Премиум профиль активирован.",
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
        "profile_text": "🧾 The 'My profile' section is under development.",
        "premium_text": "💎 The Premium section is under development.",
        "complain_text": "⚠️ Send your complaint in one message, and the administrator will receive it.",
        "complaint_sent": "✅ Complaint sent to the administrator.",
        "send_file_now": "📎 Now you can send your file.",
        "premium_profile_activated": "💎 Premium profile activated.",
    },
    "de": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Wähle eine Aktion 👇",
        "task": "Aufgabe erledigen🙏",
        "tutor": "Ich brauche einen Tutor💪",
        "menu_btn": "📋 Menü",
        "profile": "👤 Mein Profil",
        "premium": "⭐ Premium",
        "complain": "🚫 Beschwerde einreichen",
        "language": "🌍 Sprache",
        "back": "⬅️ Zurück",
        "one": "Eine Aufgabe",
        "complex": "Komplexe Arbeit",
        "premium_profile": "Premium-Profil",
        "premium_profile_info": "Einen ganzen Monat lang hast du unbegrenzten Zugang zu Aufgaben in jedem Schulfach",
        "pay_premium_profile_btn": "Premium-Profil bezahlen (2500⭐)",
        "choose_service": "👇 Wähle einen Service",
        "pay_success_task": "✅ Zahlung von 200⭐ war erfolgreich.",
        "pay_success_complex": "✅ Zahlung von 600⭐ war erfolgreich.",
        "pay_success_premium_profile": "✅ Zahlung von 2500⭐ für das Premium-Profil war erfolgreich.",
        "file_sent": "📩 Datei wurde an den Administrator gesendet.",
        "no_payment": "❌ Bitte zuerst bezahlen.",
        "tutor_reply": "💪 Schreibe, welchen Tutor du brauchst.",
        "profile_text": "🧾 Der Bereich „Mein Profil“ ist in Entwicklung.",
        "premium_text": "💎 Der Premium-Bereich ist in Entwicklung.",
        "complain_text": "⚠️ Schreibe deine Beschwerde in einer Nachricht, und der Administrator erhält sie.",
        "complaint_sent": "✅ Beschwerde wurde an den Administrator gesendet.",
        "send_file_now": "📎 Jetzt kannst du deine Datei senden.",
        "premium_profile_activated": "💎 Premium-Profil aktiviert.",
    },
    "fr": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Choisissez une action 👇",
        "task": "Faire le devoir🙏",
        "tutor": "J’ai besoin d’un tuteur💪",
        "menu_btn": "📋 Menu",
        "profile": "👤 Mon profil",
        "premium": "⭐ Premium",
        "complain": "🚫 Se plaindre",
        "language": "🌍 Langue",
        "back": "⬅️ Retour",
        "one": "Un devoir",
        "complex": "Travail complexe",
        "premium_profile": "Profil premium",
        "premium_profile_info": "Pendant tout le mois, tu auras un accès illimité aux devoirs de n’importe quelle matière scolaire",
        "pay_premium_profile_btn": "Payer le profil premium (2500⭐)",
        "choose_service": "👇 Choisissez un service",
        "pay_success_task": "✅ Le paiement de 200⭐ a réussi.",
        "pay_success_complex": "✅ Le paiement de 600⭐ a réussi.",
        "pay_success_premium_profile": "✅ Le paiement de 2500⭐ pour le profil premium a réussi.",
        "file_sent": "📩 Fichier envoyé à l’administrateur.",
        "no_payment": "❌ Vous devez payer d’abord.",
        "tutor_reply": "💪 Écris quel type de tuteur tu veux.",
        "profile_text": "🧾 La section « Mon profil » est en développement.",
        "premium_text": "💎 La section Premium est en développement.",
        "complain_text": "⚠️ Écris ta plainte dans un seul message, et l’administrateur la recevra.",
        "complaint_sent": "✅ Plainte envoyée à l’administrateur.",
        "send_file_now": "📎 Maintenant tu peux envoyer ton fichier.",
        "premium_profile_activated": "💎 Profil premium activé.",
    },
    "it": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Scegli un’azione 👇",
        "task": "Esegui il compito🙏",
        "tutor": "Ho bisogno di un tutor💪",
        "menu_btn": "📋 Menu",
        "profile": "👤 Il mio profilo",
        "premium": "⭐ Premium",
        "complain": "🚫 Reclamo",
        "language": "🌍 Lingua",
        "back": "⬅️ Indietro",
        "one": "Un compito",
        "complex": "Lavoro complesso",
        "premium_profile": "Profilo premium",
        "premium_profile_info": "Per tutto il mese avrai accesso illimitato ai compiti di qualsiasi materia scolastica",
        "pay_premium_profile_btn": "Paga profilo premium (2500⭐)",
        "choose_service": "👇 Scegli un servizio",
        "pay_success_task": "✅ Pagamento di 200⭐ riuscito.",
        "pay_success_complex": "✅ Pagamento di 600⭐ riuscito.",
        "pay_success_premium_profile": "✅ Pagamento di 2500⭐ per il profilo premium riuscito.",
        "file_sent": "📩 File inviato all’amministratore.",
        "no_payment": "❌ Devi prima pagare.",
        "tutor_reply": "💪 Scrivi di quale tutor hai bisogno.",
        "profile_text": "🧾 La sezione 'Il mio profilo' è in sviluppo.",
        "premium_text": "💎 La sezione Premium è in sviluppo.",
        "complain_text": "⚠️ Scrivi il tuo reclamo in un solo messaggio e l’amministratore lo riceverà.",
        "complaint_sent": "✅ Reclamo inviato all’amministratore.",
        "send_file_now": "📎 Ora puoi inviare il file.",
        "premium_profile_activated": "💎 Profilo premium attivato.",
    },
    "es": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Elige una acción 👇",
        "task": "Hacer la tarea🙏",
        "tutor": "Necesito un tutor💪",
        "menu_btn": "📋 Menú",
        "profile": "👤 Mi perfil",
        "premium": "⭐ Premium",
        "complain": "🚫 Quejarse",
        "language": "🌍 Idioma",
        "back": "⬅️ Atrás",
        "one": "Una tarea",
        "complex": "Trabajo complejo",
        "premium_profile": "Perfil premium",
        "premium_profile_info": "Durante todo el mes tendrás acceso ilimitado a tareas de cualquier materia escolar",
        "pay_premium_profile_btn": "Pagar perfil premium (2500⭐)",
        "choose_service": "👇 Elige un servicio",
        "pay_success_task": "✅ El pago de 200⭐ fue exitoso.",
        "pay_success_complex": "✅ El pago de 600⭐ fue exitoso.",
        "pay_success_premium_profile": "✅ El pago de 2500⭐ para el perfil premium fue exitoso.",
        "file_sent": "📩 Archivo enviado al administrador.",
        "no_payment": "❌ Primero debes pagar.",
        "tutor_reply": "💪 Escribe qué tipo de tutor necesitas.",
        "profile_text": "🧾 La sección 'Mi perfil' está en desarrollo.",
        "premium_text": "💎 La sección Premium está en desarrollo.",
        "complain_text": "⚠️ Escribe tu queja en un solo mensaje y el administrador la recibirá.",
        "complaint_sent": "✅ Queja enviada al administrador.",
        "send_file_now": "📎 Ahora puedes enviar tu archivo.",
        "premium_profile_activated": "💎 Perfil premium activado.",
    },
    "fi": {
        "language_text": (
            "👋 Вибери мову бота\n"
            "👋 Select the bot language\n"
            "👋 Выберите язык бота\n"
            "👋 Valitse botin kieli"
        ),
        "home": "Valitse toiminto 👇",
        "task": "Suorita tehtävä🙏",
        "tutor": "Tarvitsen opettajan💪",
        "menu_btn": "📋 Valikko",
        "profile": "👤 Oma profiili",
        "premium": "⭐ Premium",
        "complain": "🚫 Valita",
        "language": "🌍 Kieli",
        "back": "⬅️ Takaisin",
        "one": "Yksi tehtävä",
        "complex": "Laaja työ",
        "premium_profile": "Premium-profiili",
        "premium_profile_info": "Koko kuukauden ajan saat rajattoman määrän tehtäviä mistä tahansa kouluaineesta",
        "pay_premium_profile_btn": "Maksa premium-profiili (2500⭐)",
        "choose_service": "👇 Valitse palvelu",
        "pay_success_task": "✅ 200⭐ maksu onnistui.",
        "pay_success_complex": "✅ 600⭐ maksu onnistui.",
        "pay_success_premium_profile": "✅ 2500⭐ maksu premium-profiilista onnistui.",
        "file_sent": "📩 Tiedosto lähetettiin ylläpitäjälle.",
        "no_payment": "❌ Sinun täytyy maksaa ensin.",
        "tutor_reply": "💪 Kirjoita, millaisen opettajan tarvitset.",
        "profile_text": "🧾 Osio 'Oma profiili' on kehitteillä.",
        "premium_text": "💎 Premium-osio on kehitteillä.",
        "complain_text": "⚠️ Kirjoita valituksesi yhteen viestiin, niin ylläpitäjä saa sen.",
        "complaint_sent": "✅ Valitus lähetettiin ylläpitäjälle.",
        "send_file_now": "📎 Nyt voit lähettää tiedoston.",
        "premium_profile_activated": "💎 Premium-profiili aktivoitu.",
    },
}

for extra_lang in ["kk", "id", "ms", "km", "pl", "pt", "uz"]:
    TEXTS[extra_lang] = dict(TEXTS["en"])


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

    if user_lang_manual.get(user_id):
        return user_lang.get(user_id, "ua")

    detected_lang = detect_user_language(message.from_user.language_code)
    if detected_lang:
        user_lang[user_id] = detected_lang
        return detected_lang

    if user_id in user_lang:
        return user_lang[user_id]

    user_lang[user_id] = "ua"
    return "ua"


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


def get_extra_menu(lang: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["profile"])
    kb.row(TEXTS[lang]["premium"])
    kb.row(TEXTS[lang]["complain"])
    kb.row(TEXTS[lang]["language"])
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
    detected_lang = detect_user_language(message.from_user.language_code)

    if detected_lang:
        user_lang[message.from_user.id] = detected_lang
        user_state[message.from_user.id] = "main"
        await message.answer(TEXTS[detected_lang]["home"], reply_markup=get_main_menu(detected_lang))
        return

    user_state[message.from_user.id] = "start_language"
    await message.answer(TEXTS["ua"]["language_text"], reply_markup=get_language_keyboard())


@dp.message_handler(commands=["myprofile"])
async def cmd_myprofile(message: types.Message):
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "profile_screen"
    await message.answer(TEXTS[lang]["profile_text"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["premium"])
async def cmd_premium(message: types.Message):
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "premium_screen"
    await message.answer(TEXTS[lang]["premium_text"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["complaint"])
async def cmd_complaint(message: types.Message):
    lang = resolve_user_language(message)
    user_state[message.from_user.id] = "complaint_wait"
    await message.answer(TEXTS[lang]["complain_text"], reply_markup=get_back_only_menu(lang))


@dp.message_handler(commands=["language"])
async def cmd_language(message: types.Message):
    user_lang_manual.pop(message.from_user.id, None)
    user_state[message.from_user.id] = "language_menu"
    current_lang = resolve_user_language(message)
    await message.answer(
        TEXTS[current_lang]["language_text"],
        reply_markup=get_language_keyboard(include_back=True, lang=current_lang)
    )


@dp.message_handler(lambda m: m.text in LANG_BUTTONS)
async def set_language(message: types.Message):
    lang = LANG_BUTTONS[message.text]
    previous_state = user_state.get(message.from_user.id, "start_language")

    user_lang[message.from_user.id] = lang
    user_lang_manual[message.from_user.id] = True

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
    lang = resolve_user_language(message)
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

    elif payload == "premium_profile_payment":
        user_payment[message.from_user.id] = "premium_profile"
        user_state[message.from_user.id] = "main"
        await message.answer(
            f"{TEXTS[lang]['pay_success_premium_profile']}\n\n{TEXTS[lang]['premium_profile_activated']}",
            reply_markup=get_main_menu(lang)
        )


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    lang = resolve_user_language(message)

    if message.from_user.id not in user_payment:
        await message.answer(TEXTS[lang]["no_payment"])
        return

    order_type = user_payment[message.from_user.id]

    if order_type == "premium_profile":
        await message.answer(TEXTS[lang]["premium_profile_activated"], reply_markup=get_main_menu(lang))
        return

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
    lang = resolve_user_language(message)
    state = user_state.get(message.from_user.id, "main")
    text = message.text

    if text == TEXTS[lang]["back"]:
        if state in [
            "task_menu", "extra_menu", "tutor_screen", "profile_screen",
            "premium_screen", "complaint_wait", "awaiting_file",
            "premium_profile_screen"
        ]:
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
        user_lang_manual.pop(message.from_user.id, None)
        user_state[message.from_user.id] = "language_menu"
        current_lang = resolve_user_language(message)
        await message.answer(
            TEXTS[current_lang]["language_text"],
            reply_markup=get_language_keyboard(include_back=True, lang=current_lang)
        )
        return

    await message.answer(TEXTS[lang]["home"], reply_markup=get_main_menu(lang))


async def on_startup(_):
    await set_bot_commands()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)