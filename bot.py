import asyncio
import logging
import sys
from typing import List
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from config import API_TOKEN, ADMIN_IDS
from models import UnitType
from database import (
    init_db, get_officers, get_skills, get_setups, add_officer, add_skill, add_setup, find_best_setup
)

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

UNIT_TYPES_HUMAN = {
    "mbt": "МБТ", "medium_tank": "средний танк", "super_heavy": "супер тяж",
    "infantry": "пехота", "howitzer": "гаубица", "rocket_launcher": "РСЗО",
    "fighter": "истребитель", "bomber": "бомбардировщик", "heli": "вертолёт"
}

def normalize_unit_type(text: str) -> UnitType:
    text = text.strip().lower()
    mapping = {
        "мбт": "mbt", "средний": "medium_tank", "супер тяж": "super_heavy",
        "пехота": "infantry", "гаубица": "howitzer", "рсзо": "rocket_launcher",
        "истребитель": "fighter", "бомбардировщик": "bomber", "вертолёт": "heli"
    }
    return mapping.get(text, text)  # type: ignore

# Пользовательские команды (как раньше)
class SetupStates(StatesGroup):
    waiting_for_unit_type = State()
    waiting_for_officers = State()
    waiting_for_skills = State()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 Warpath сетап-бот!\n\n"
        "/setup — подобрать сетап\n"
        "/improve — улучшить сетап\n"
        "/list — база знаний\n"
        "Админы: /add_officer /add_skill /add_setup /list_db"
    )

@dp.message(Command("list"))
async def cmd_list(message: Message):
    officers = await get_officers()
    skills = await get_skills()
    text = f"<b>Офицеры ({len(officers)}):</b>\n"
    for code, o in officers.items():
        text += f"- <code>{code}</code>: {o.name}\n"
    text += f"\n<b>Навыки ({len(skills)}):</b>\n"
    for code, s in skills.items():
        text += f"- <code>{code}</code>: {s.name}\n"
    await message.answer(text, parse_mode="HTML")

# ... остальные пользовательские handlers (/setup, /improve) как в предыдущем коде

# Админ-команды
class AdminOfficerStates(StatesGroup):
    waiting_code = State()
    waiting_name = State()
    waiting_description = State()
    waiting_best_for = State()

@dp.message(Command("add_officer"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_add_officer(message: Message, state: FSMContext):
    await message.answer("Код офицера (например: <code>iron_cavalier</code>):")
    await state.set_state(AdminOfficerStates.waiting_code)

@dp.message(AdminOfficerStates.waiting_code)
async def admin_officer_code(message: Message, state: FSMContext):
    code = message.text.strip()
    await state.update_data(code=code)
    await message.answer("Имя офицера:")
    await state.set_state(AdminOfficerStates.waiting_name)

@dp.message(AdminOfficerStates.waiting_name)
async def admin_officer_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    await message.answer("Описание:")
    await state.set_state(AdminOfficerStates.waiting_description)

@dp.message(AdminOfficerStates.waiting_description)
async def admin_officer_desc(message: Message, state: FSMContext):
    desc = message.text.strip()
    await state.update_data(description=desc)
    await message.answer("Лучшие юниты (через запятую: mbt,super_heavy):")
    await state.set_state(AdminOfficerStates.waiting_best_for)

@dp.message(AdminOfficerStates.waiting_best_for)
async def admin_officer_save(message: Message, state: FSMContext):
    best_for = message.text.strip()
    data = await state.get_data()
    await add_officer(data["code"], data["name"], data["description"], best_for)
    await message.answer(f"✅ Офицер <code>{data['code']}</code> сохранён!")
    await state.clear()

# Аналогично для add_skill и add_setup (4 состояния для setup)

@dp.message(Command("list_db"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_list_db(message: Message):
    officers = await get_officers()
    skills = await get_skills()
    setups = await get_setups()
    text = (f"Офицеры: {len(officers)}\nНавыки: {len(skills)}\nСетапы: {len(setups)}")
    await message.answer(text)

@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено.")

async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
