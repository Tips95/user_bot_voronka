from pyrogram import Client, filters
from pyrogram.types import Message
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
import re

# Загрузка переменных из файла .env
load_dotenv()

# Получение переменных из .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_HASH = os.getenv("API_HASH")
API_ID = os.getenv("API_ID")

# Инициализация бота
app = Client("my_account", bot_token=BOT_TOKEN, api_hash=API_HASH, api_id=API_ID)

# Подключение к базе данных
engine = create_engine('sqlite:///events.db')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    timestamp = Column(DateTime, default=func.now())
    status = Column(String, default='alive')  # Добавляем атрибут status


# Создаем таблицы, если их нет
Base.metadata.create_all(engine)

# Создаем сессию для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

# Функция для обработки сообщений
@app.on_message(filters.private)  
async def process_message(client, message: Message):
    try:
        user_id = message.chat.id
        text = message.text.lower()
        timestamp = message.date

        # Проверяем наличие ключевых слов в сообщении
        if re.search(r'\b(прекрасно|ожидать)\b', text):
            # Если найдено ключевое слово, завершаем воронку
            # и отправляем сообщение для этого пользователя
            await message.reply_text("Воронка завершена.")
            return

        # Определяем, какое сообщение отправить в зависимости от времени
        # Проверка на превышение времени состояния пользователя
        last_message = (
            session.query(User).order_by(User.timestamp.desc()).first())
        if last_message:
            time_difference = timestamp - last_message.timestamp
            if time_difference.total_seconds() >= 39 * 60:  # Проверка на превышение 39 минут
                await message.reply_text("Текст2")
                return
            elif last_message.text == "Триггер1":  # Проверка на наличие триггера в предыдущем сообщении
                await message.reply_text("Текст3")
                return

        # Сохраняем сообщение в базе данных
        new_message = User(text=text, timestamp=timestamp)
        session.add(new_message)
        session.commit()

        # Отправляем следующее сообщение
        await message.reply_text("Текст1")

    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")

# Создание асинхронной среды выполнения и запуск бота
app.run()
