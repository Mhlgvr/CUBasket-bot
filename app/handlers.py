# import asyncio
from os import getenv

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

import app.database as sq
import app.keyboards as kb
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
    add_thread = State()


about_tournament = '''CU Backetball Tournament – внутренний турнир среди студентов и сотрудников Центрального университета, организованный баскетбольным клубом ЦБК. Вступай в команду своего потока или приходи болеть за друзей!

За событиями турнира можно следить в канале Центрального Баскетбольного клуба. Туда будет скидываться расписание матчей, результаты, статистика и медиа-контент.
Ссылка на канал:
https://t.me/+HyTgxx-lv3pkNmQy

====🟠 Регламент турнира 🟠==== 

*** Формат турнира ***
В турнире будут принимать участие от 6 до 8 команд (возможно разделение потока на две команды), они будут разделены на 2 группы. В каждой команде от 3 до 5 человек. 
Игры каждый с каждым в группе. Путём жеребьёвки мы определим последовательность игр и объявим все туры группового этапа до плей-офф. 
Плей-офф будет отыгран с 1/4 стадии (все команды выходят из группы). У команд будет минимум 2 игровых дня, максимум 3.

*** Процесс начисления очков ***
В групповом этапе за игры начисляются очки в турнирной таблице:
Победа – 3 очка; Победа в овертайме – 2 очка; Поражение – 1 очко.
В случае равного количества очков места разделяются между командами по итогам личной встречи.

*** Формат проведения игр ***
Матчи 15 минут на групповом этапе и 22 минуты в плей-офф с остановками времени при штрафных бросках и таймаутах.
Формат 3х3 на два кольца, при бросковом фоле штрафные броски предусмотрены.
Очки считаются по системе 1/2, у каждой команды на игру 2 таймаута. В случае равного счёта время продлевается.

📅 Игровые даты: 
1, 8, 15 марта 
Все игры проводятся по субботам с 12:00 до 15:00.

📍 Адрес: 
метро Таганская, ул. Марксистская, 22с2
Спортивный зал Campus "Таганка"'''


@router.message(CommandStart())
async def start_menu(message: Message):
    check = await user_exists(message.from_user.id)
    if not check:
        await message.answer("""
🏀 Привет! 🏀

🤖 Я бот-распределитель для участников турнира по баскетболу в ЦУ. Через меня ты можешь узнать все про турнир и присоединиться к команде своего потока.
📣 Присоединяйся к команде своего потока или приходи болеть за друзей! 🔥
🏅 Победителей ждут уникальные призы
💡 И помни: не важно, профи ты или новичок — главное желание играть и наслаждаться игрой! 🏆
        """, reply_markup=kb.start)
    else:
        await main_menu(message)


@router.callback_query(F.data == 'join')
async def reg_1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.name)
    await callback.answer()
    await callback.message.edit_text(
        'Напиши свои имя и фамилию', reply_markup=kb.back1)


@router.message(Reg.name)
async def reg_2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.thread)
    await message.answer(
        'Выбери поток: ', reply_markup=await kb.teams())


@router.callback_query(Reg.thread, F.data)
async def reg_3(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == 'back_to_start':
        await go_to_start(callback, state)
    await state.update_data(thread=callback.data)
    data = await state.get_data()
    await sq.add_user(
        callback.from_user.id,
        callback.from_user.username,
        data['name'],
        data['thread'])
    await callback.message.edit_text(
        'Добро пожаловать в команду!', reply_markup=kb.menu)
    await state.clear()


@router.message(Command('menu'))
async def main_menu(message: Message):
    await message.answer(
        'Ждем тебя на турнире!', reply_markup=kb.menu)


@router.callback_query(F.data == 'info1')
async def get_info1(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        about_tournament, reply_markup=kb.info1)


@router.callback_query(F.data == 'info2')
async def get_info2(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        about_tournament, reply_markup=kb.info2)


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
    await callback.message.edit_text(
        'Твоя команда: \n' + team_name + '\n' + '\n'.join(data),
        reply_markup=kb.team_menu)


@router.callback_query(F.data == 'edit_team_name')
async def edit_team_name_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.team_name)
    await callback.message.edit_text(
        'Напиши новое название', reply_markup=kb.back2)


@router.message(Admin.team_name)
async def edit_team_name_2(message: Message, state: FSMContext):
    await state.clear()
    await sq.edit_team_name(message.from_user.id, message.text)
    await message.answer(
        'Название команды изменено', reply_markup=kb.menu)


@router.callback_query(F.data == 'leave')
async def leave_team_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Confirm.leaving)
    await callback.message.edit_text(
        'Ты точно хочешь уйти?', reply_markup=kb.answer)


@router.callback_query(Confirm.leaving)
async def leave_team_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    if callback.data == 'yes':
        await sq.delete_user(callback.from_user.id)
        await callback.message.edit_text(
            'Вы покинули команду', reply_markup=kb.start)
    else:
        await callback.message.delete()
        await main_menu(callback.message)


@router.message(Command('admin'))
async def admin_panel(message: Message):
    user_id = message.from_user.id
    if str(user_id) == ADMIN_ID:
        await message.answer(
            'ADMIN PANEL', reply_markup=kb.admin)
    else:
        await message.reply('ты не админ')


@router.callback_query(F.data == 'back_to_admin')
async def go_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        'ADMIN PANEL', reply_markup=kb.admin)


@router.callback_query(F.data == 'all_teams')
async def get_all_teams(callback: CallbackQuery):
    data = await sq.get_teams_info()
    await callback.answer()
    await callback.message.answer(data, reply_markup=kb.admin)


@router.callback_query(F.data == 'edit_info')
async def edit_info_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.info)
    await callback.message.edit_text(
        'SEND NEW INFORMATION', reply_markup=kb.back3)


@router.message(Admin.info)
async def edit_info_2(message: Message, state: FSMContext):
    await state.clear()
    global about_tournament
    about_tournament = message.text
    await message.answer(
        'INFORMATION UPDATED', reply_markup=kb.admin)


@router.callback_query(F.data == 'send_message')
async def send_message_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.send_message)
    await callback.message.edit_text(
        'ENTER MESSAGE', reply_markup=kb.back3)


@router.message(Admin.send_message)
async def send_message_2(message: Message, state: FSMContext):
    await state.clear()
    text = message.text
    ids = await sq.get_user_ids()
    bot = message.bot
    for user_id in ids:
        await bot.send_message(user_id, text)
    await message.answer('MESSAGE SENT', reply_markup=kb.admin)


@router.callback_query(F.data == 'add_thread')
async def add_thread_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.add_thread)
    await callback.message.edit_text(
        'SEND THREAD AND TEAM NAME SEPARATED BY _', reply_markup=kb.back3)


@router.message(Admin.add_thread)
async def add_thread_2(message: Message, state: FSMContext):
    await state.clear()
    thread, team_name = message.text.split('_')
    await sq.add_thread(thread, team_name)
    await message.answer('THREAD ADDED', reply_markup=kb.admin)
