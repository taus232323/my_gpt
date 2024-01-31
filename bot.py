import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from settings import TOKEN
import g4f
import asyncio

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot.log', filemode='w')


class ChatBot:

    def __init__(self) -> None:
        self.history = {}
        self.model = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        text = f"Привет, {user.first_name}. "
        await update.message.reply_text(text)
        self.history[user.id] = []
        await self.choose_version(context, update)

    async def help(self, update: Update) -> None:
        await update.message.reply_text("Бот только развивается и сейчас он может только отвечать на текстовые сообщения")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        loop = asyncio.get_running_loop()
        if user.id not in self.history:
            self.history[user.id] = []
        role = "user"
        text = update.message.text
        self.update_history(user_id=user.id, role=role, text=text)

        await context.bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        model_response = await loop.run_in_executor(None, self.get_model_response, user.id, text)

        await update.message.reply_text(model_response)
        self.update_history(user.id, "assistant", model_response)
        self.autoclear_history(user.id)

    async def handle_button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        if query.data == "gpt_35":
            await context.bot.send_message(update.effective_chat.id, 
                                           "Ты выбрал версию ChatGPT-3.5 Turbo в ней доступен режим диалога. "
                                           "Теперь введи свой запрос")
            await context.bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
            await context.bot.delete_message(update.effective_chat.id, update.effective_message.message_id - 1)
            self.model = 35
        elif query.data == "gpt_4":
            await context.bot.send_message(update.effective_chat.id, "Ты выбрал версию ChatGPT-4. Теперь введи свой запрос")
            await context.bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
            self.model = 4


    async def choose_version(self, context: ContextTypes.DEFAULT_TYPE, update: Update) -> None:
        m_chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        gpt_35 = InlineKeyboardButton("GPT-3.5 Turbo", callback_data="gpt_35")
        gpt_4 = InlineKeyboardButton("GPT-4", callback_data="gpt_4")
        reply_markup = InlineKeyboardMarkup([[gpt_35], [gpt_4]])
        text = "Для продолжения выбери модель"
        await update.message.reply_text(text, reply_markup=reply_markup)
        await context.bot.delete_message(m_chat_id, message_id)
        # await context.bot.delete_message(m_chat_id, message_id - 1)

    def update_history(self, user_id, role, text) -> None:
        message = {"role": role, "content": text}
        self.history[user_id].append(message)

    def autoclear_history(self, user_id) -> None:
        if len(self.history[user_id]) > 15000:
            self.history[user_id] = self.history[user_id][-10000:]

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        self.clear_history(user_id)
        await update.message.reply_text("История чата очищена")

    def clear_history(self, user_id) -> None:
        self.history[user_id] = []

    def get_model_response(self, user_id, text) -> str:
        if self.model:
            if self.model == 35:
                response = g4f.ChatCompletion.create(
                    model=g4f.models.gpt_35_turbo_16k,
                    messages=self.history[user_id],
                )
            elif self.model == 4:
                response = g4f.ChatCompletion.create(
                    model=g4f.models.gpt_4_turbo,
                    messages={"role": "user", "content": text},
                )
            else:
                return "Выберите модель сначала"
            return response

    def run(self):
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("clear", self.clear_history))

        app.add_handler(CallbackQueryHandler(self.handle_button_click))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = Bot()
    bot.run()
