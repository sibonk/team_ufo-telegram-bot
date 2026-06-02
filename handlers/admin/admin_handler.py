from aiogram import Router, F, Bot
from aiogram.types import (Message, CallbackQuery,
                           ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from db.models import db
import handlers.user.keyboard as user_kb

router = Router()

pgsize = 4
markup_label = {"open": "Открыт", "in_progress": "Ожидается", "closed": "Закрыт",}

admin_panel_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Обращения"), KeyboardButton(text="Назад")]
], resize_keyboard=True)

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Создать обращение"), KeyboardButton(text="Мои обращения")],
    [KeyboardButton(text="Админ-панель")]
], resize_keyboard=True)

def is_admin(tg_id: int) -> bool:
    row = db.fetchone("SELECT admin FROM users WHERE tg_id = ?", (tg_id,))
    return bool(row and row["admin"] == 1)

def build_admin_tickets_kb(tickets: list, page: int, total: int) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i, t in enumerate(tickets):
        row.append(InlineKeyboardButton(text=f"{user_kb.categories[t['category']]} • #{t['id']}", callback_data=f"admin_view_{t['id']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    total_pages = (total + pgsize - 1) // pgsize
    nav = []
    nav.append(InlineKeyboardButton(text="◀️", callback_data=f"admin_page_{page - 1}" if page > 0 else "admin_nav_locked"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="admin_nav_locked"))
    nav.append(InlineKeyboardButton(text="▶️", callback_data=f"admin_page_{page + 1}" if (page + 1) * pgsize < total else "admin_nav_locked"))
    rows.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=rows)

async def send_admin_tickets_page(target, page: int, edit: bool = False):
    total_row = db.fetchone("SELECT COUNT(*) FROM tickets WHERE status IN ('open', 'in_progress')")
    total = total_row[0] if total_row else 0

    if total == 0:
        text = "Хорошая работа :) Пока нет обращений."
        if edit:
            if target.message.photo or target.message.video or target.message.document:
                await target.message.delete()
                await target.message.answer(text)
            else:
                await target.message.edit_text(text)
            await target.answer()
        else:
            await target.answer(text)
        return

    max_pgsize = max((total - 1) // pgsize, 0)
    page = max(0, min(page, max_pgsize))
    offset = page * pgsize

    tickets = db.fetchall("SELECT id, category, tg_id FROM tickets WHERE status IN ('open', 'in_progress') ORDER BY created_at ASC LIMIT ? OFFSET ?", (pgsize, offset))
    total_pages = (total + pgsize - 1) // pgsize
    markup = build_admin_tickets_kb(tickets, page, total)
    caption = f"Всего обращений: {total} | Страница {page + 1}/{total_pages}"

    if edit:
        if target.message.photo or target.message.video or target.message.document:
            await target.message.delete()
            await target.message.answer(caption, reply_markup=markup)
        else:
            await target.message.edit_text(caption, reply_markup=markup)
        await target.answer()
    else:
        await target.answer(caption, reply_markup=markup)

@router.message(F.text == "Админ-панель")
async def open_admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Вы вошли как администратор, выберите действие", reply_markup=admin_panel_kb)

@router.message(F.text == "Обращения")
async def admin_open_tickets(message: Message):
    if not is_admin(message.from_user.id):
        return
    await send_admin_tickets_page(message, page=0, edit=False)

@router.message(F.text == "Назад")
async def admin_back(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Главное меню", reply_markup=main_kb)

@router.callback_query(F.data.startswith("admin_page_"))
async def admin_navigate(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    page = int(callback.data.split("_")[-1])
    await send_admin_tickets_page(callback, page=page, edit=True)

@router.callback_query(F.data == "admin_nav_locked")
async def admin_nav_locked(callback: CallbackQuery):
    await callback.answer("^_^")

@router.callback_query(F.data.startswith("admin_view_"))
async def admin_view_ticket(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    ticket_id = int(callback.data.split("_")[-1])
    ticket = db.fetchone("SELECT t.id, t.category, t.problem, t.photo_id, t.status, t.created_at, t.tg_id, u.username FROM tickets t JOIN users u ON t.tg_id = u.tg_id WHERE t.id = ?", (ticket_id,))

    if not ticket:
        await callback.answer("Тикет не найден", show_alert=True)
        return

    markup_labell = markup_label.get(ticket["status"], ticket["status"])
    if ticket["status"] == "open":
        action_btn = InlineKeyboardButton(text="✅ Рассмотреть", callback_data=f"admin_review_{ticket_id}")
    else:
        action_btn = InlineKeyboardButton(text="🔒 Закрыть", callback_data=f"admin_close_{ticket_id}")
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ Назад", callback_data="admin_back_to_list")],
        [action_btn]
    ])

    username = f"@{ticket['username']}" if ticket["username"] else f"tg_id: {ticket['tg_id']}"
    text = (f"Категория: *{user_kb.categories[ticket['category']]}*    Уникальный номер: *#{ticket['id']}*\n\nОтправитель: {username}\nОписание проблемы: {ticket['problem']}\n\nОбращение открыто: *{ticket['created_at']}*\nСтатус: {markup_labell}")

    if ticket["photo_id"]:
        await callback.message.delete()
        await callback.message.answer_photo(photo=ticket["photo_id"], caption=text, parse_mode="Markdown", reply_markup=markup)
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_review_"))
async def admin_review_ticket(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    ticket_id = int(callback.data.split("_")[-1])
    ticket = db.fetchone("SELECT tg_id, category FROM tickets WHERE id = ?", (ticket_id,))
    if not ticket:
        await callback.answer("Тикет не найден", show_alert=True)
        return

    db.query("UPDATE tickets SET status = 'in_progress' WHERE id = ?", (ticket_id,))
    try:
        await callback.bot.send_message(chat_id=ticket["tg_id"], text=(f"🔔 Ура! Администратор взялся за ваше обращение *#{ticket_id}*"), parse_mode="Markdown")
    except Exception:
        pass

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ Назад", callback_data="admin_back_to_list")],
        [InlineKeyboardButton(text="🔒 Закрыть", callback_data=f"admin_close_{ticket_id}")]
    ])

    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass

    await callback.answer()

@router.callback_query(F.data.startswith("admin_close_"))
async def admin_close_ticket(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    ticket_id = int(callback.data.split("_")[-1])
    ticket = db.fetchone("SELECT tg_id, category FROM tickets WHERE id = ?", (ticket_id,))
    if not ticket:
        await callback.answer("Тикет не найден", show_alert=True)
        return

    db.query("UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,))
    try:
        await callback.bot.send_message(chat_id=ticket["tg_id"], text=(f"🔔 Ваше обращение *#{ticket_id}* ({user_kb.categories[ticket['category']]}) закрыто.\nЕсли проблема не решена , создайте новое обращение."), parse_mode="Markdown")
    except Exception:
        pass

    if callback.message.photo or callback.message.video or callback.message.document:
        await callback.message.delete()
        await callback.message.answer(f"Вы закрыли обращение - *#{ticket_id}*.", parse_mode="Markdown")
    else:
        await callback.message.edit_text(f"Вы закрыли обращение - *#{ticket_id}*.", parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "admin_back_to_list")
async def admin_back_to_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await send_admin_tickets_page(callback, page=0, edit=True)