import logging
from settings import TOKEN
from telegram import Update
import asyncio
import os
import g4f
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot.log', filemode='w')

welcome_message = "Добро пожаловать в бота с поддержкой ChatGPT4. Введи свой запрос в поле для ввода"

class Bot:
    
    def __init__(self) -> None:
        self.history = {}
        self.animation_path = os.path.join(os.path.dirname(__file__),'melding_circles.gif')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        text = f"Привет, {user.first_name}. " + welcome_message
        await update.message.reply_text(text)
        self.history[user.id] = []

    async def help(self, update: Update) -> None:
        await update.message.reply_text("Бот только развивается и сейчас он может только отвечать на текстовые сообщения")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        loop = asyncio.get_running_loop()
        self.update_history(user_id=user.id, role='user', text=update.message.text)
        
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        
        result = await loop.run_in_executor(None, self.get_gpt4_response, user.id)
        await update.message.reply_text(result)
        self.update_history(user.id, 'assistant', result)
        print(self.history[user.id])
    
    def update_history(self, user_id, role, text) -> None:
        if role == "user":
            message = {"role": "user", "content": text}
        elif role == "assistant":
            message = {"role": "assistant", "content": text}
        self.history[user_id].append(message)
        
    def get_gpt4_response(self, user_id) -> str:
        response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4_32k,
        messages=self.history[user_id],
    )
        return response
        
    def run(self):
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = Bot()
    bot.run()
