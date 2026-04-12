import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice
from aiogram.utils import executor

API_TOKEN = 8311783439:AAFN3ldS9NXPZZ8zhvf2XFViYxVx6aKL368
OWNER_ID = 510644962  # your Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Store user language and payment status
user_lang = {}
user_payment = {}  # user_id: 'task' or 'complex'

# Texts for all languages
TEXTS = {
    'ua': {
        'start': 'Вітаю з підпискою! 👋\n\nВибери мову бота',
        'task': 'Виконати завдання🙏',
        'tutor': 'Потрібен репетитор💪',
        'one': 'Одне завдання',
        'complex': 'Комплексне виконання роботи',
        'pay_success': '✅ Оплата пройшла! Надішли файл.',
        'file_sent': '📩 Файл відправлено!',
        'no_payment': '❌ Спочатку потрібно оплатити!'
    },
    'en': {
        'start': 'Congratulations on subscribing! 👋\n\nSelect the bot language',
        'task': 'Do the task🙏',
        'tutor': 'Need a tutor💪',
        'one': 'Single task',
        'complex': 'Complex work',
        'pay_success': '✅ Payment successful! Send your file.',
        'file_sent': '📩 File sent!',
        'no_payment': '❌ You must pay first!'
    },
    'ru': {
        'start': 'Поздравляем с подпиской! 👋\n\nВыберите язык бота',
        'task': 'Выполнить задание🙏',
        'tutor': 'Нужен репетитор💪',
        'one': 'Одно задание',
        'complex': 'Комплексная работа',
        'pay_success': '✅ Оплата прошла! Отправьте файл.',
        'file_sent': '📩 Файл отправлен!',
        'no_payment': '❌ Сначала нужно оплатить!'
    },
    'fi': {
        'start': 'Onnittelut tilauksestasi! 👋\n\nValitse botin kieli',
        'task': 'Suorita tehtävä🙏',
        'tutor': 'Tarvitsetko opettajan💪',
        'one': 'Yksi tehtävä',
        'complex': 'Laajempi työ',
        'pay_success': '✅ Maksu onnistui! Lähetä tiedosto.',
        'file_sent': '📩 Tiedosto lähetetty!',
        'no_payment': '❌ Sinun täytyy maksaa ensin!'
    }
}

# Language keyboard
lang_kb = ReplyKeyboardMarkup(resize_keyboard=True)
lang_kb.add(KeyboardButton('Українська'), KeyboardButton('English'))
lang_kb.add(KeyboardButton('Русский'), KeyboardButton('Suomi'))

LANG_MAP = {
    'Українська': 'ua',
    'English': 'en',
    'Русский': 'ru',
    'Suomi': 'fi'
}

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    text = """Вітаю з підпискою! 👋 

Вибери мову бота
Congratulations on subscribing! 👋
Select the bot language
Поздравляем с подпиской! 👋
Выберите язык бота
Onnittelut tilauksestasi! 👋
Valitse botin kieli"""
    await msg.answer(text, reply_markup=lang_kb)

@dp.message_handler(lambda m: m.text in LANG_MAP)
async def set_language(msg: types.Message):
    lang = LANG_MAP[msg.text]
    user_lang[msg.from_user.id] = lang

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(TEXTS[lang]['task'], TEXTS[lang]['tutor'])

    await msg.answer(TEXTS[lang]['start'], reply_markup=kb)

@dp.message_handler()
async def menu(msg: types.Message):
    lang = user_lang.get(msg.from_user.id, 'ua')

    if msg.text == TEXTS[lang]['task']:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(TEXTS[lang]['one'], TEXTS[lang]['complex'])
        await msg.answer('👇', reply_markup=kb)

    elif msg.text == TEXTS[lang]['one']:
        await bot.send_invoice(
            chat_id=msg.chat.id,
            title="Task Payment",
            description="Single task",
            payload="task_payment",
            currency="XTR",
            prices=[LabeledPrice(label="Task", amount=100)],
            start_parameter="task"
        )

    elif msg.text == TEXTS[lang]['complex']:
        await bot.send_invoice(
            chat_id=msg.chat.id,
            title="Complex Payment",
            description="Complex work",
            payload="complex_payment",
            currency="XTR",
            prices=[LabeledPrice(label="Complex", amount=500)],
            start_parameter="complex"
        )

# Pre-checkout
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

# Successful payment
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def got_payment(msg: types.Message):
    lang = user_lang.get(msg.from_user.id, 'ua')

    payload = msg.successful_payment.invoice_payload

    if payload == 'task_payment':
        user_payment[msg.from_user.id] = 'task'
    elif payload == 'complex_payment':
        user_payment[msg.from_user.id] = 'complex'

    await msg.answer(TEXTS[lang]['pay_success'])

# File handler with payment check
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_file(msg: types.Message):
    lang = user_lang.get(msg.from_user.id, 'ua')

    if msg.from_user.id not in user_payment:
        await msg.answer(TEXTS[lang]['no_payment'])
        return

    order_type = user_payment[msg.from_user.id]

    caption = f"📥 New order: {order_type}\nUser: {msg.from_user.id}"

    await bot.send_document(OWNER_ID, msg.document.file_id, caption=caption)

    await msg.answer(TEXTS[lang]['file_sent'])

    # Reset payment after file sent
    del user_payment[msg.from_user.id]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
