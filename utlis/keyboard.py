from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Создать заявку"), KeyboardButton(text="Мои заявки")]
], resize_keyboard=True, input_field_placeholder="Выберите меню")

create_ticket = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Не работает техника", callback_data="ticket_tech"), InlineKeyboardButton(text="Проблема с интернетом",callback_data="ticket_inter")],
    [InlineKeyboardButton(text="Установка ПО", callback_data="ticket_soft"), InlineKeyboardButton(text="Другая помощь", callback_data="ticket_other")]
])

categories = { "tech": "Не работает техника", "inter": "Проблема с интернетом", "soft": "Установка ПО", "other": "Другая помощь" }

confirm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✍ Изменить", callback_data="confirm_edit"), InlineKeyboardButton(text="📩 Отправить", callback_data="confirm_conf")]
])