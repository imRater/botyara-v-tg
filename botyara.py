import asyncio
import random
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- 1. НАЛАШТУВАННЯ АЙДІ ТА ТОКЕН ---
TOKEN = "8778267324:AAGGVuhVeML3S1vGcPEKi_9fcePo6XaQZOc"
ADMIN_GROUP_ID = -1003712184305
FRACTION_GROUP_ID = -1003630431013

ROBLOX_THREAD = 410
STAFF_THREAD = 486

THREADS = {
    "НПС": 10, "НГС": 25, "СУД": 13, "СБС": 4, "АДВОКАТ": 20, "ПРОКУРОР": 16
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Form(StatesGroup): 
    waiting_for_data = State()

# --- 2. ТЕКСТИ АНКЕТ ---
ANKETAS = {
    "НПС": "📌 **Анкета на НПС**\n▫️Вік:\n▫️РП-вік:\n◽Нік Roblox:\n🌟Адекватність (0/10):\n🕐Готові грати годину на день?:\n📢Будете допомагати з рейдами?:\n🌟Готові до суду, а не в тюрму?:\n🌟Відпустите, якщо виправдають?:\n⭐Знання правил (0/10):\n⭐Вміння РП (0/10):",
    "НГС": "🛡️ **Анкета до НГС:**\n1. Нік Roblox:\n2. Вік:\n3. Готові до дисципліни?:\n4. Стрільба (0/10):\n5. Чому НГС?",
    "СУД": "⚖️ **Анкета на Суддю:**\n1. Нік Roblox:\n2. Вік:\n3. Знання законів (0/10):\n4. Обіцяєте бути чесним?:\n5. Витримка?",
    "СБС": "🥷 **Анкета до СБС:**\n1. Нік Roblox:\n2. Навички тактики (0/10):\n3. Досвід у силових структурах?:\n4. Готові захищати лідерів?:\n5. Онлайн?",
    "АДВОКАТ": "💼 **Анкета на Адвоката:**\n1. Нік Roblox:\n2. Знаєте права затриманих?:\n3. Вміння переконувати (0/10):\n4. Досвід РП:",
    "ПРОКУРОР": "👔 **Анкета на Прокурора:**\n1. Нік Roblox:\n2. Мета на посаді?:\n3. Уважність до дрібниць?:\n4. Готові до виступів у суді?",
    "ЛИДЕР": "👑 **Анкета на Лідера:**\n1. Нік Roblox:\n2. Фракція:\n3. Плани (мінімум 3):\n4. Є своя команда?:\n5. Вік та Discord:",
    "АДМИН": "🛠️ **Анкета на Адміна:**\n1. Нік Roblox:\n2. Знання правил (0/10):\n3. Скільки годин онлайн?:\n4. Чому ми?\n5. Вік:"
}

# --- 3. КЛАВІАТУРИ ---
def main_m():
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🏢 Вступити во Фракцію", callback_data="open_fractions"))
    b.row(types.InlineKeyboardButton(text="👑 Подати на Лідера/Адміна", callback_data="open_staff"))
    return b.as_markup()

def fraction_m():
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="🚔 НПС", callback_data="apply_НПС"), types.InlineKeyboardButton(text="🛡️ НГС", callback_data="apply_НГС"))
    b.row(types.InlineKeyboardButton(text="⚖️ Суддя", callback_data="apply_СУД"), types.InlineKeyboardButton(text="🥷 СБС", callback_data="apply_СБС"))
    b.row(types.InlineKeyboardButton(text="💼 Адвокат", callback_data="apply_АДВОКАТ"), types.InlineKeyboardButton(text="👔 Прокурор", callback_data="apply_ПРОКУРОР"))
    b.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    return b.as_markup()

# --- 4. ОБРОБНИКИ БОТА ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("👋 **UA_NORTH_RP**\nОберіть розділ:", reply_markup=main_m())

@dp.callback_query(F.data == "open_fractions")
async def fractions(c: types.CallbackQuery):
    await c.message.edit_text("🏛 Оберіть фракцію:", reply_markup=fraction_m())

@dp.callback_query(F.data == "open_staff")
async def staff(c: types.CallbackQuery):
    b = InlineKeyboardBuilder()
    b.row(types.InlineKeyboardButton(text="👑 Лідером", callback_data="apply_ЛИДЕР"), types.InlineKeyboardButton(text="🛡️ Адміном", callback_data="apply_АДМИН"))
    b.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    await c.message.edit_text("⚙️ Заявки в персонал:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("apply_"))
async def start_anketa(c: types.CallbackQuery, state: FSMContext):
    target = c.data.split("_")[1]
    await state.update_data(target=target)
    await state.set_state(Form.waiting_for_data)
    await c.message.answer(ANKETAS.get(target, "Пишіть анкету:"), parse_mode="Markdown")

@dp.message(Form.waiting_for_data)
async def process_anketa(m: types.Message, state: FSMContext):
    data = await state.get_data(); target = data.get("target")
    chat_id, thread_id = (ADMIN_GROUP_ID, STAFF_THREAD) if target in ["ЛИДЕР", "АДМИН"] else (FRACTION_GROUP_ID, THREADS.get(target, 1))
    try:
        await bot.send_message(chat_id, f"📩 **Анкета: {target}**\nВід: @{m.from_user.username}\n\n{m.text}", message_thread_id=thread_id)
        await m.reply("✅ Надіслано!")
    except: await m.reply("❌ Помилка. Перевір права бота.")
    await state.clear()

@dp.callback_query(F.data == "back")
async def back(c: types.CallbackQuery):
    await c.message.edit_text("👋 Меню:", reply_markup=main_m())

# --- 5. ВЕБ-СЕРВЕР (KEEP ALIVE) ---
async def handle(request):
    return web.Response(text="UA_NORTH_RP BOT IS ALIVE 🚀")

async def run_web():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Порт 8080 стандарт для таких сервісів
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

# --- 6. ГОЛОВНИЙ ЗАПУСК ---
async def main():
    # Запускаємо веб-сервер одночасно з ботом
    await run_web()
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Бот запущено разом з веб-сервером!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())