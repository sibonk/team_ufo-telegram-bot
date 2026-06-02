from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="backtomain")]
])

confirm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить", callback_data="edit"), InlineKeyboardButton(text="Отправить", callback_data="send")]
])