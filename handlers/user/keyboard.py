from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

create_ticket = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Не работает техника", callback_data="ticket_tech"), InlineKeyboardButton(text="Проблема с интернетом",callback_data="ticket_inter")],
    [InlineKeyboardButton(text="Установка ПО", callback_data="ticket_soft"), InlineKeyboardButton(text="Другая помощь", callback_data="ticket_other")]
])

categories = { "tech": "Не работает техника", "inter": "Проблема с интернетом", "soft": "Установка ПО", "other": "Другая помощь" }