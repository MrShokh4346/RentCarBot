import asyncio
import logging
import sys
import os
from dotenv.main import load_dotenv


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
    print(status)
    print(call)
    print(url_by_id+call.split(":")[0])
    res = requests.put(url_by_id+call.split(":")[0], json={"status":status})
    if res.status_code == 204:
        await callback.answer(text="Updated!",
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
        types.KeyboardButton(text="Confirmed orders"),
        types.KeyboardButton(text="Don't confirmed orders")
    ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Select order status"
    )
    await message.answer("Select order status", reply_markup=keyboard)


@dp.message(lambda message: message.text.lower() == "don't confirmed orders")
async def get_dont_confirmed_orders(message: types.Message) -> None:
    res = requests.get(url+"?status=0")
    orders = json.loads(res.content)
    if len(orders) == 0:
        await message.answer("Nothing found")
    for order in orders:
        resp = f" id : {order['id']}\n Customer name : {order['customer_name']}\n Contact number : {order['contact_number']}\n Brand : {order['car_brand']}\n Model : {order['car_model']}\n Child sit : {order['child_sit']}\n Delivery : {order['delivery']}\n"
        resp += f" Pick-up date : {order['from_date']}\n Drop-off date : {order['to_date']}\n Pick-up location : {order['from_destination']}\n Drop-off location : {order['to_destination']}\n Status : {order['status']}"
        button = [[types.InlineKeyboardButton(text="Update status", callback_data=f"obj_{order['id']}:t")]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
        await message.answer(resp, reply_markup=keyboard)


@dp.message(lambda message: message.text.lower() == 'confirmed orders')
async def get_confirmed_orders(message: types.Message) -> None:
    res = requests.get(url+"?status=1")
    orders = json.loads(res.content)
    if len(orders) == 0:
        await message.answer("Nothing found")
    for order in orders:
        resp = f" id : {order['id']}\n Customer name : {order['customer_name']}\n Contact number : {order['contact_number']}\n Brand : {order['car_brand']}\n Model : {order['car_model']}\n Child sit : {order['child_sit']}\n Delivery : {order['delivery']}\n"
        resp += f" Pick-up date : {order['from_date']}\n Drop-off date : {order['to_date']}\n Pick-up location : {order['from_destination']}\n Drop-off location : {order['to_destination']}\n Status : {order['status']}"
        button = [[types.InlineKeyboardButton(text="Update status", callback_data=f"obj_{order['id']}:f")]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=button)
        await message.answer(resp, reply_markup=keyboard)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())