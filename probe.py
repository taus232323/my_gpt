<<<<<<< HEAD
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from settings import TOKEN

from response import get_response


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w', filename='bot.log')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, который использует GPT-4 для ответов на ваши вопросы. Просто напишите мне что-нибудь.")

@dp.message_handler()
async def handle_message(message: types.Message):
    response = await get_response(message.text)
    
    # Отправляем ответ пользователю
    await message.answer(response)

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
=======
>>>>>>> c546355c978e4e7fd3895c999d818d5d75d2591f
