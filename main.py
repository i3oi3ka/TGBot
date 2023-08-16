import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler
from datetime import datetime, timedelta

TOKEN_BOT = '6562178126:AAFnLXiXgGj9D2cClMm1akj0Ej5M8Td7t7w'
user_data = dict()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Command start was triggered")
    await update.message.reply_text(
        "Welcome to my Expense Bot!\n"
        "Commands: \n"
        "\n"
    )


def run():
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("Application build successfully!")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))

    app.run_polling()


if __name__ == '__main__':
    run()
