# import asyncio
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
# from sqlalchemy.testing.config import any_async

import app.keyboards as kb
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.database as sq

from dotenv import load_dotenv
from os import getenv

from app.database import user_exists

load_dotenv()
ADMIN_ID = getenv("ADMIN_ID")

router = Router()

class Reg(StatesGroup):
    name = State()
    thread = State()

class Confirm(StatesGroup):
    leaving = State()

class Admin(StatesGroup):
    team_name = State()
    info = State()
    send_message = State()


about_tournament = '''информация о турнире'''

@router.message(CommandStart())
async def start_menu(message: Message):
    if not user_exists(message.from_user.id):
        await message.answer("""
        Привет! 
        Присоединяйся к своей команде на первом баскетбольном турнире Центрального университета!
        """, reply_markup=kb.start)
    else:
        await main_menu(message)


@router.callback_query(F.data == 'join')
async def reg_1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.name)
    await callback.answer()
    await callback.message.edit_text('Напиши свои имя и фамилию', reply_markup=kb.back1)

@router.message(Reg.name)
async def reg_2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.thread)
    await message.answer('Выберите поток: ', reply_markup=await kb.teams())

@router.callback_query(Reg.thread, F.data)
async def reg_3(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == 'back_to_start':
        await go_to_start(callback, state)
    await state.update_data(thread=callback.data)
    data = await state.get_data()
    await sq.add_user(callback.from_user.id, callback.from_user.username, data['name'], data['thread'])
    await callback.message.edit_text(f'Добро пожаловать в команду!', reply_markup=kb.menu)
    await state.clear()

@router.message(Command('menu'))
async def main_menu(message: Message):
    await message.answer('Ждем тебя на турнире!', reply_markup=kb.menu)

@router.callback_query(F.data == 'info1')
async def get_info1(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(about_tournament, reply_markup=kb.info1)

@router.callback_query(F.data == 'info2')
async def get_info2(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(about_tournament, reply_markup=kb.info2)


@router.callback_query(F.data == 'back_to_start')
async def go_to_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    await start_menu(callback.message)

@router.callback_query(F.data == 'back_to_menu')
async def go_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await state.clear()
    await main_menu(callback.message)


@router.callback_query(F.data == 'team')
async def get_my_team(callback: CallbackQuery):
    await callback.answer()
    data = await sq.get_team_members(callback.from_user.id)
    team_name = await sq.get_team_name(callback.from_user.id)
    await callback.message.edit_text('Твоя команда: \n' + team_name + '\n' + '\n'.join(data), reply_markup=kb.team_menu)

@router.callback_query(F.data == 'edit_team_name')
async def edit_team_name_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.team_name)
    await callback.message.edit_text('Напиши новое название', reply_markup=kb.back2)

@router.message(Admin.team_name)
async def edit_team_name_2(message: Message, state: FSMContext):
    await state.clear()
    await sq.edit_team_name(message.from_user.id, message.text)
    await message.answer('Название команды изменено', reply_markup=kb.menu)



@router.callback_query(F.data == 'leave')
async def leave_team_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Confirm.leaving)
    await callback.message.edit_text('Ты точно хочешь уйти?', reply_markup=kb.answer)


@router.callback_query(Confirm.leaving)
async def leave_team_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    if callback.data == 'yes':
        await sq.delete_user(callback.from_user.id)
        await callback.message.edit_text('Вы покинули команду', reply_markup=kb.start)
    else:
        await callback.message.delete()
        await main_menu(callback.message)


@router.message(Command('admin'))
async def admin_panel(message: Message):
    user_id = message.from_user.id
    if str(user_id) == ADMIN_ID:
        await message.answer('ADMIN PANEL', reply_markup=kb.admin)
    else:
        await message.reply('ты не админ')

@router.callback_query(F.data == 'back_to_admin')
async def go_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('ADMIN PANEL', reply_markup=kb.admin)

@router.callback_query(F.data == 'all_teams')
async def get_all_teams(callback: CallbackQuery):
    data = await sq.get_teams_info()
    await callback.answer()
    await callback.message.answer(data, reply_markup=kb.admin)

@router.callback_query(F.data == 'edit_info')
async def edit_info_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.info)
    await callback.message.edit_text('SEND NEW INFORMATION', reply_markup=kb.back3)

@router.message(Admin.info)
async def edit_info_2(message: Message, state: FSMContext):
    await state.clear()
    global about_tournament
    about_tournament = message.text
    await message.answer('INFORMATION UPDATED', reply_markup=kb.admin)

@router.callback_query(F.data == 'send_message')
async def send_message_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.send_message)
    await callback.message.edit_text('ENTER MESSAGE', reply_markup=kb.back3)

@router.message(Admin.send_message)
async def send_message_2(message: Message, state: FSMContext):
    await state.clear()
    text = message.text
    ids = await sq.get_user_ids()
    bot = message.bot
    for user_id in ids:
        await bot.send_message(user_id, text)
    await message.answer("MESSAGE SENT", reply_markup=kb.admin)
