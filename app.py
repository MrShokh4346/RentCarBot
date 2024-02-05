import asyncio
import logging
import sys
import os
from dotenv.main import load_dotenv
# from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import requests
import json

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.environ['BOT_TOKEN']

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
url = 'https://rentcar.pythonanywhere.com/rent/v1/orders'
url_by_id = 'https://rentcar.pythonanywhere.com/rent/v1/order/'


@dp.callback_query(F.data.startswith("obj_"))
async def callbacks_num(callback: types.CallbackQuery):
    call = callback.data.split("_")[1]
    status = True if call.split(":")[1] == 't' else False
    res = requests.put(url_by_id+call.split(":")[0], json={"status":status})
    if res.status_code == 204:
        await callback.answer(text="O'zgartirildi!",
        show_alert=True
        )
    else:
        await callback.answer(text="Something went wrong!!!",
        show_alert=True
        )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    kb = [
    [
        types.KeyboardButton(text="Tasdiqlangan buyurtmalar"),
        types.KeyboardButton(text="Tasdiqlanmagan buyurtmalar")
    ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer("Buyurtmalar statusini tanlang", reply_markup=keyboard)


@dp.message(lambda message: message.text.lower() == "tasdiqlanmagan buyurtmalar")
async def get_dont_confirmed_orders(message: types.Message) -> None:
    res = requests.get(url+"?status=0")
    orders = json.loads(res.content)
    if len(orders) == 0:
        await message.answer("Hechnarsa topilmadi")
    for order in orders:
        resp = f" <b>Buyutmachi</b> : {order['customer_name']}\n"
        resp += f"    Aloqa uchun: {order['contact_number']}\n"
        resp += f"<b>Avtomobil</b> : {order['car_brand']} {order['car_model']}\n"
        resp += f"    Xavfsizlik orindigi : {'kerak' if order['child_sit']==True else 'kerak emas'}\n"
        resp += f"    Yetkazib berish : {'kerak' if order['delivery']==True else 'kerak emas'}\n"
        resp += f"    Olib ketish sanasi : {order['from_date']}\n" if order.get('from_date') is not None else ''
        resp += f"    Qaytarish sanasi : {order['to_date']}\n" if order.get('to_date') is not None else ''
        resp += f"    Olib ketish joyi : {order['from_destination']}\n" if order.get('from_destination') is not None else ''
        resp += f"    Qaytarish joyi : {order['to_destination']}\n" if order.get('to_destination') is not None else ''
        resp += f"    Buyurtma holati : {'tasdiqlandi' if order['status']==True else 'tasdiqlanmadi'}"
        button = [[types.InlineKeyboardButton(text="Buyurtma holatini o'zgartirish", callback_data=f"obj_{order['id']}:t")]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
        await message.answer(resp, reply_markup=keyboard)


@dp.message(lambda message: message.text.lower() == 'tasdiqlangan buyurtmalar')
async def get_confirmed_orders(message: types.Message) -> None:
    res = requests.get(url+"?status=1")
    orders = json.loads(res.content)
    if len(orders) == 0:
        await message.answer("Hechnarsa topilmadi")
    for order in orders:
        resp = f" <b>Buyutmachi</b> : {order['customer_name']}\n"
        resp += f"    Aloqa uchun: {order['contact_number']}\n"
        resp += f"<b>Avtomobil</b> : {order['car_brand']} {order['car_model']}\n"
        resp += f"    Xavfsizlik orindigi : {'kerak' if order['child_sit']==True else 'kerak emas'}\n"
        resp += f"    Yetkazib berish : {'kerak' if order['delivery']==True else 'kerak emas'}\n"
        resp += f"    Olib ketish sanasi : {order['from_date']}\n" if order.get('from_date') is not None else ''
        resp += f"    Qaytarish sanasi : {order['to_date']}\n" if order.get('to_date') is not None else ''
        resp += f"    Olib ketish joyi : {order['from_destination']}\n" if order.get('from_destination') is not None else ''
        resp += f"    Qaytarish joyi : {order['to_destination']}\n" if order.get('to_destination') is not None else ''
        resp += f"    Buyurtma holati : {'tasdiqlandi' if order['status']==True else 'tasdiqlanmadi'}"
        button = [[types.InlineKeyboardButton(text="Buyurtma holatini o'zgartirish", callback_data=f"obj_{order['id']}:f")]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
        await message.answer(resp, reply_markup=keyboard)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # session = AiohttpSession(proxy='http://proxy.server:3128')
    # bot = Bot(token=TOKEN, session=session, parse_mode=ParseMode.HTML)
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())