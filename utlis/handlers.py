from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import utlis.keyboard as kb
from database import create_ticket, get_user_tickets

router = Router()

class Ticket(StatesGroup):
    problem = State()
    confirm = State()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(photo="AgACAgIAAxkBAANfah5_Nkam0AwQBrR9rWYsWuyT8eIAAnEhaxtZ5flIEFi8aktJ_1YBAAMCAAN5AAM7BA", 
                               caption="Система заявок IT-отдела\n\nЧерез этого бота Вы можете: сообщить о проблеме и отследить статус обращения.", reply_markup=kb.main)

@router.message(F.text == "Создать заявку")
async def create_tick(message: Message):
    await message.answer("Выберите необходимую категорию помощи:", reply_markup=kb.create_ticket)

@router.callback_query(F.data.startswith("ticket_"))
async def ticket_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]

    await state.update_data(category=category)
    await state.set_state(Ticket.problem)
    await callback.message.edit_text(f"📁 Категория: {kb.categories[category]}\n\nОпишите вашу проблему, по желанию можете прикрепить фото.")
    await callback.answer()

@router.message(Ticket.problem)
async def hookproblem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    data = await state.get_data()

    await state.set_state(Ticket.confirm)
    await message.answer(f"Проверьте данные перед отправкой!\n\n▸ Категория: {kb.categories[data['category']]}\n▸ Проблема: {data['problem']}", reply_markup=kb.confirm)

@router.callback_query(F.data == "confirm_conf")
async def confirm_ticket(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ticket_id = create_ticket(user_id=callback.from_user.id, username=callback.from_user.username, category=kb.categories[data["category"]], problem=data["problem"])

    await callback.message.edit_text(f"✅ Заявка №{ticket_id} успешно создана.\n\nКатегория: {kb.categories[data['category']]}")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "confirm_edit")
async def edit_ticket(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Ticket.problem)
    await callback.message.edit_text("Введите новое описание проблемы:")
    await callback.answer()

@router.message(F.text == "Мои заявки")
async def my_tickets(message: Message):
    tickets = get_user_tickets(message.from_user.id)
    if not tickets:
        await message.answer("У вас пока нет заявок.")
        return
    text = "📋 Ваши заявки:\n\n"
    for ticket_id, category, status, created_at in tickets:
        text += (f"▸ Проблема: {ticket_id}\nСтатус: {status}\n\n")
    await message.answer(text)

# @router.message(F.photo)
# async def get_photo_id(message: Message):
#     await message.answer(f"ID photo: {message.photo[-1].file_id}")