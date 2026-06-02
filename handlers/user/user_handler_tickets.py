from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from db.models import db
import handlers.user.keyboard as kb

router = Router()

pgsize = 2
markup_label = {"open": "Открыт", "in_progress": "Ожидается", "closed": "Закрыт",}

def build_tickets_keyboard(tickets: list, page: int, total: int) -> InlineKeyboardMarkup:
    rows = []
    ticket_buttons = [InlineKeyboardButton(text=f"{kb.categories[t['category']]} • #{t['id']}", callback_data=f"view_ticket_{t['id']}")
        for t in tickets
    ]
    rows.append(ticket_buttons)

    nav_inactive = total <= pgsize
    rows.append([InlineKeyboardButton(text="◀️", callback_data=f"tickets_page_{page - 1}" if not nav_inactive and page > 0 else "nav_locked"),
                 InlineKeyboardButton(text="▶️", callback_data=f"tickets_page_{page + 1}" if not nav_inactive and (page + 1) * pgsize < total else "nav_locked"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

async def send_tickets_page(target, tg_id: int, page: int, edit: bool = False):
    total_row = db.fetchone("SELECT COUNT(*) FROM tickets WHERE tg_id = ?", (tg_id,))
    total = total_row[0] if total_row else 0

    if total == 0:
        text = "Создайте обращение, нажав на кнопку ниже."
        if edit:
            if target.message.photo or target.message.video or target.message.document:
                await target.message.delete()
                await target.message.answer(text)
            else:
                await target.message.edit_text(text)
        else:
            await target.answer(text)
        return

    max_page = max((total - 1) // pgsize, 0)
    page = max(0, min(page, max_page))

    offset = page * pgsize
    tickets = db.fetchall("SELECT id, category, problem, status, created_at FROM tickets WHERE tg_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (tg_id, pgsize, offset))

    total_pages = (total + pgsize - 1) // pgsize
    markup = build_tickets_keyboard(tickets, page, total)
    caption = f"Страница {page + 1}/{total_pages}"

    if edit:
        if target.message.photo or target.message.video or target.message.document:
            await target.message.delete()
            await target.message.answer(caption, reply_markup=markup)
        else:
            await target.message.edit_text(caption, reply_markup=markup)
        await target.answer()
    else:
        await target.answer(caption, reply_markup=markup)

@router.message(F.text == "Мои обращения")
async def my_tickets(message: Message):
    await send_tickets_page(message, message.from_user.id, page=0, edit=False)

@router.callback_query(F.data.startswith("tickets_page_"))
async def navigate_tickets(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await send_tickets_page(callback, callback.from_user.id, page=page, edit=True)

@router.callback_query(F.data == "nav_locked")
async def nav_locked(callback: CallbackQuery):
    await callback.answer("🔐")

@router.callback_query(F.data.startswith("view_ticket_"))
async def view_ticket(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[-1])
    ticket = db.fetchone("SELECT id, category, problem, photo_id, status, created_at FROM tickets WHERE id = ? AND tg_id = ?", (ticket_id, callback.from_user.id))

    if not ticket:
        await callback.answer("Данный тикет удален", show_alert=True)
        return

    markup_labell = markup_label.get(ticket["status"], ticket["status"])
    back_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_tickets")]
    ])

    text = (f"Дата создания обращения: *{ticket['created_at']}*\nКатегория: *{kb.categories[ticket['category']]}*    Уникальный номер: *#{ticket['id']}*\n\nОписание проблемы: {ticket['problem']}\n\nСтатус: {markup_labell}")
    if ticket["photo_id"]:
        await callback.message.delete()
        await callback.message.answer_photo(photo=ticket["photo_id"], caption=text, parse_mode="Markdown", reply_markup=back_btn)
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_btn)

    await callback.answer()

@router.callback_query(F.data == "back_to_tickets")
async def back_to_tickets(callback: CallbackQuery):
    await send_tickets_page(callback, callback.from_user.id, page=0, edit=True)