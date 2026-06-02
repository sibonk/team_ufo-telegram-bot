from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import handlers.user.keyboard as kb
import handlers.markup_keyboard as kbs
from db.models import db

router = Router()

class Ticket(StatesGroup):
    problem = State()
    conf = State()

@router.message(F.text == "Создать обращение")
async def hook_ticket_create(message: Message):
    count = db.fetchone("SELECT COUNT(*) FROM tickets WHERE tg_id = ? AND status != 'closed'", (message.from_user.id,))
    if count and count[0] >= 6:
        await message.answer("Вы создаете слишком много обращений. Ожидайте пока ответят на предыдущие.")
        return
    await message.answer("Выберите категорию:", reply_markup=kb.create_ticket)

@router.callback_query(F.data.startswith("ticket_"))
async def ticket_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    await state.set_state(Ticket.problem)
    await callback.message.edit_text(text=f"📁 Категория: {kb.categories[category]}\n\nОпишите вашу проблему, по желанию можете прикрепить фото.", reply_markup=kbs.back)
    await callback.answer()

@router.message(Ticket.problem, F.photo)
async def hookproblem_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    text = message.caption or ""

    await state.update_data(problem=text, photo_id=photo_id, user_msg_id=message.message_id)
    data = await state.get_data()
    await state.set_state(Ticket.conf)

    bot_msg = await message.answer(f"⚠ Проверьте данные перед отправкой!\n\n▸ Категория: {kb.categories[data['category']]}\n▸ Проблема: {data['problem']}\n▸ Фото: прикреплено 📎", reply_markup=kbs.confirm)
    await state.update_data(bot_msg_id=bot_msg.message_id)

@router.message(Ticket.problem, F.text)
async def hookproblem_text(message: Message, state: FSMContext):
    await state.update_data(problem=message.text, photo_id=None, user_msg_id=message.message_id)
    data = await state.get_data()
    await state.set_state(Ticket.conf)

    bot_msg = await message.answer(f"⚠ Проверьте данные перед отправкой!\n\n▸ Категория: {kb.categories[data['category']]}\n▸ Проблема: {data['problem']}", reply_markup=kbs.confirm)
    await state.update_data(bot_msg_id=bot_msg.message_id)

@router.callback_query(F.data == "send")
async def confirm_content(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    ticket_id = db.query("INSERT INTO tickets (tg_id, category, problem, photo_id, status) VALUES (?, ?, ?, ?, ?)", (callback.from_user.id, data["category"], data["problem"], data.get("photo_id"), "open"))

    await callback.message.edit_text(f"Ваше обращение номер {ticket_id} принято!\nВы получите уведомление здесь.")
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "edit")
async def edit_content(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=data["user_msg_id"])
    except Exception:
        pass
    await callback.message.delete()
    await state.set_state(Ticket.problem)
    await callback.answer()


@router.callback_query(F.data == "backtomain")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text="Выберите категорию:", reply_markup=kb.create_ticket)
    await callback.answer()