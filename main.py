import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.utils.media_group import MediaGroupBuilder

BOT_TOKEN = 'BOT_TOKEN'
MANAGER_ID = manager_user_id

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Registration(StatesGroup):
    choosing_tariff = State()
    choosing_date = State()
    choosing_location = State()
    choosing_phone = State()

def make_keyboard(with_cancel=False):
    builder = ReplyKeyboardBuilder()
    if with_cancel:
        builder.add(types.KeyboardButton(text="❌ Отмена"))
        builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для регистрации. Используй команду /reg для начала регистрации "
        "или /tariffs для просмотра галереи."
    )

@dp.message(Command("cancel"))
@dp.message(F.text.lower() == "отмена")
@dp.message(F.text.lower() == "❌ отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активной регистрации для отмены.")
        return
    
    await state.clear()
    await message.answer(
        "Регистрация отменена.",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(Command("reg"))
async def cmd_reg(message: types.Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Standart"))
    builder.add(types.KeyboardButton(text="Plus"))
    builder.add(types.KeyboardButton(text="VIP"))
    builder.add(types.KeyboardButton(text="❌ Отмена"))
    builder.adjust(1, 2)
    
    await message.answer(
        "Выберите тариф:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(Registration.choosing_tariff)

@dp.message(Registration.choosing_tariff)
async def tariff_chosen(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await cmd_cancel(message, state)
        return
        
    if message.text not in ["Standart", "Plus", "VIP"]:
        await message.answer("Пожалуйста, выберите тариф, используя кнопки ниже.")
        return
    
    await state.update_data(tariff=message.text)
    await message.answer(
        "Введите дату в формате день.месяц:",
        reply_markup=make_keyboard(with_cancel=True)
    )
    await state.set_state(Registration.choosing_date)

@dp.message(Registration.choosing_date)
async def date_chosen(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await cmd_cancel(message, state)
        return
    
    await state.update_data(date=message.text)
    await message.answer(
        "Введите место:",
        reply_markup=make_keyboard(with_cancel=True)
    )
    await state.set_state(Registration.choosing_location)

@dp.message(Registration.choosing_location)
async def location_chosen(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await cmd_cancel(message, state)
        return
    
    await state.update_data(location=message.text)
    await message.answer(
        "Введите номер телефона:",
        reply_markup=make_keyboard(with_cancel=True)
    )
    await state.set_state(Registration.choosing_phone)

@dp.message(Registration.choosing_phone)
async def phone_chosen(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await cmd_cancel(message, state)
        return
    
    await state.update_data(phone=message.text)
    user_data = await state.get_data()
    
    user_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
    
    msg = (
        "✨ <b>Новая регистрация</b> ✨\n"
        f"👤 Пользователь: {user_link} (@{message.from_user.username})\n"
        f"📊 Тариф: {user_data['tariff']}\n"
        f"📅 Дата: {user_data['date']}\n"
        f"📍 Место: {user_data['location']}\n"
        f"📱 Телефон: {user_data['phone']}"
    )
    
    await bot.send_message(
        MANAGER_ID,
        msg,
        parse_mode="HTML"
    )
    
    await message.answer(
        "✅ Спасибо! Мы свяжемся с вами в ближайшее время.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()

@dp.message(Command("tariffs"))
async def cmd_galery(message: types.Message):

    # Standart
    standart_builder = MediaGroupBuilder(
        caption="📦 Standart\n💵 350 сомони\n\n🧸 1 аниматор\n⏱️ 30 минут\n🎭 Мини-сценка"
    )
    standart_builder.add_photo(media="AgACAgIAAxkBAAMZaBxKvRsEwdcPQvHUG0_2PzHkBEcAApHsMRsHS-lI3jDpKXyp-a8BAAMCAANzAAM2BA")
        
    # PLUS
    plus_builder = MediaGroupBuilder(
        caption="✨ Plus\n💵 650 сомони\n\n🧸 2 аниматора\n⏰ 1 час\n🎉 Игры и шоу"
    )
    plus_builder.add_photo(media="AgACAgIAAxkBAAMbaBxKvVkfCTnedRUM4FtgyWB7VwgAApDsMRsHS-lI5bISFeTjoOUBAAMCAANzAAM2BA")

    # VIP
    vip_builder = MediaGroupBuilder(
        caption="👑 VIP\n💵 1000 сомони\n\n🧸 3 аниматора\n⏳ 2 часа\n🎬 Полная программа"
    )
    vip_builder.add_photo(media="AgACAgIAAxkBAAMaaBxKvSyWBtcItA9KJUDsCF6a-KcAApLsMRsHS-lILR4DmSwdXooBAAMCAANzAAM2BA")

    await message.answer_media_group(
        media=standart_builder.build()
    )
    await message.answer_media_group(
        media=plus_builder.build()
    )
    await message.answer_media_group(
        media=vip_builder.build()
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
