from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database as sq


start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='О турнире', callback_data='info1')],
    [InlineKeyboardButton(text='Вступить в команду', callback_data='join')]
])

info1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вступить в команду', callback_data='join')],
    [InlineKeyboardButton(text='Назад', callback_data='back_to_start')]
])

info2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Моя команда', callback_data='team')],
    [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
])

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Моя команда', callback_data='team')],
    [InlineKeyboardButton(text='О турнире', callback_data='info2')],
    [InlineKeyboardButton(text='Покинуть команду', callback_data='leave')]
])

team_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить название',
                          callback_data='edit_team_name')],
    [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')],
    [InlineKeyboardButton(text='Покинуть команду', callback_data='leave')]
])

back1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='назад', callback_data='back_to_start')],
])

back2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='отмена', callback_data='back_to_menu')],
])

back3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='return', callback_data='back_to_admin')],
])

answer = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='да', callback_data='yes'),
    InlineKeyboardButton(text='нет', callback_data='no')]
])


async def teams():
    keyboard = InlineKeyboardBuilder()
    threads = await sq.get_threads()
    for thread in threads:
        keyboard.add(InlineKeyboardButton(text=thread, callback_data=thread))
    keyboard.add(InlineKeyboardButton(text='назад',
                                      callback_data='back_to_start'))
    return keyboard.adjust(1).as_markup()

admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='TEAMS', callback_data='all_teams')],
    [InlineKeyboardButton(text='UPDATE INFO', callback_data='edit_info')],
    [InlineKeyboardButton(text='SEND MESSAGE', callback_data='send_message')],
    [InlineKeyboardButton(text='ADD THREAD', callback_data='add_thread')],
    [InlineKeyboardButton(text='CALL DATABASE', callback_data='make_query')]
])
