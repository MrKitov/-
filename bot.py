import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from telethon.sync import TelegramClient

# Телеграм-данные (замени своими)
API_ID = 27662006  # Твой API ID из my.telegram.org
API_HASH = "64be3da191471db68ef69b728a677bf6"  # Твой API HASH
SESSION_NAME = "anon"  # Название сессии Telethon (создастся файл anon.session)

# Токен бота
TOKEN = "7689644925:AAFq-B3A7rRfyTYbREelzx-YafgF5NGPMYQ"

# Файл с настройками
CONFIG_FILE = "config.json"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализируем Telethon-клиент
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
client.start()

# Клавиатура для настроек
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Задать автоответ")],
        [KeyboardButton(text="📇 Контакты для автоответа")],
        [KeyboardButton(text="🔄 Включить автоответчик"), KeyboardButton(text="⛔ Выключить автоответчик")],
    ], resize_keyboard=True
)

# Функция загрузки конфигурации
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"auto_reply": "Здравствуйте! Опишите ваш вопрос.", "contacts": [], "enabled": False}

# Функция сохранения конфигурации
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# Загружаем конфиг
config = load_config()

# Функция проверки, онлайн ли пользователь
async def is_user_online(username):
    try:
        user = await client.get_entity(username)
        if user.status and hasattr(user.status, 'was_online'):
            return False  # Был онлайн недавно
        return True  # Не в сети
    except Exception:
        return False  # Ошибка (например, скрытый статус)

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Добро пожаловать! Используйте кнопки для настройки автоответчика.", reply_markup=main_keyboard)

# Установка автоответа
@dp.message(lambda message: message.text == "📝 Задать автоответ")
async def set_auto_reply(message: Message):
    await message.answer("Введите новый текст автоответчика:")

# Сохранение автоответа
@dp.message(lambda message: message.text and message.text != "📝 Задать автоответ")
async def save_auto_reply(message: Message):
    config["auto_reply"] = message.text
    save_config(config)
    await message.answer(f"✅ Новый автоответ установлен:\n\"{message.text}\"")

# Добавление контакта
@dp.message(lambda message: message.text == "📇 Контакты для автоответа")
async def show_contacts(message: Message):
    contacts = "\n".join(config["contacts"]) if config["contacts"] else "Нет контактов."
    await message.answer(f"📇 Контакты для автоответа:\n{contacts}\n\nОтправьте юзернейм контакта (@username), чтобы добавить или удалить его.")

@dp.message(lambda message: message.text and message.text.startswith("@"))
async def toggle_contact(message: Message):
    contact = message.text[1:]  # Убираем "@"
    if contact in config["contacts"]:
        config["contacts"].remove(contact)
        action = "удален"
    else:
        config["contacts"].append(contact)
        action = "добавлен"
    save_config(config)
    await message.answer(f"✅ Контакт @{contact} {action} в список автоответчика.")

# Включение автоответчика
@dp.message(lambda message: message.text == "🔄 Включить автоответчик")
async def enable_auto_reply(message: Message):
    config["enabled"] = True
    save_config(config)
    await message.answer("✅ Автоответчик включен!")

# Выключение автоответчика
@dp.message(lambda message: message.text == "⛔ Выключить автоответчик")
async def disable_auto_reply(message: Message):
    config["enabled"] = False
    save_config(config)
    await message.answer("⛔ Автоответчик выключен.")

# Обработчик любых сообщений (автоответ)
@dp.message()
async def auto_reply(message: Message):
    if config["enabled"] and message.from_user.username in config["contacts"]:
        if await is_user_online(message.from_user.username):
            await message.answer(config["auto_reply"])

# Запуск бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
