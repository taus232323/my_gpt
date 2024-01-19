import logging
from settings import TOKEN
from response import get_response
from telegram import Update
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot.log', filemode='w')

welcome_message = "Добро пожаловать в бота с поддержкой ChatGPT4. Введи свой запрос в поле для ввода"

class Bot:
    
    def __init__(self) -> None:
        self.animation_path = os.path.join(os.path.dirname(__file__),'melding_circles.gif')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        text = f"Привет, {user.first_name}. " + welcome_message
        await update.message.reply_text(text)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Бот только развивается и сейчас он может только отвечать на текстовые сообщения")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_text = update.message.text
        await update.message.reply_animation(animation=open(self.animation_path, 'rb'), caption="Готовлю ответ...")
        await update.message.reply_text(get_response(user_text))
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        
    def run(self):
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = Bot()
    bot.run()
