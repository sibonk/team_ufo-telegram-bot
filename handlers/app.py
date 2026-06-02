from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from db.models import db

router = Router()

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Создать обращение"), KeyboardButton(text="Мои обращения")]
], resize_keyboard=True, input_field_placeholder="Выберите действие")

admin_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Создать обращение"), KeyboardButton(text="Мои обращения")],
    [KeyboardButton(text="Админ-панель")]
], resize_keyboard=True, input_field_placeholder="Выберите действие")


@router.message(CommandStart())
async def start(message: Message):
    user = db.fetchone("SELECT * FROM users WHERE tg_id = ?", (message.from_user.id,))
    if not user:
        db.query("INSERT INTO users (tg_id, username, admin) VALUES (?, ?, ?)", (message.from_user.id, message.from_user.username, 0))
        user = db.fetchone("SELECT * FROM users WHERE tg_id = ?", (message.from_user.id,))

    kb = admin_kb if user["admin"] == 1 else main_kb

    await message.answer_photo(photo="AgACAgIAAxkBAAIBpmoezZNvhHGwW57AcXzkkXL-YIIjAAJPI2sbWeX5SLJBylj74isYAQADAgADeQADOwQ",
        caption="ℹ️ Чтобы начать, выберите действие, нажав на одну из кнопок\n\nСоздавайте обращения в IT-отдел. Отслеживайте статус тикета.", reply_markup=kb)