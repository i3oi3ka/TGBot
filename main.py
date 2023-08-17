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


class Expense:

    def __init__(self, category: str, cost: int, date: datetime):
        self.category = category
        self.cost = cost
        self.date = date

    def __str__(self):
        return f"{self.category} {self.cost} {self.date.strftime('%Y-%m-%d %H:%M%S')}"


async def add_expense(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    expense_parts = ' '.join(context.args).split()
    expense_category = expense_parts[0]
    date_expense = expense_parts[2] + " " + expense_parts[3]
    try:
        expense_cost = int(expense_parts[1].strip())
    except ValueError:
        logging.error("Invalid cost error")
        await update.message.reply_text("Your cost argument is invalid, please enter integer num")
        return
    try:
        date = datetime.strptime(date_expense.strip(), '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print(expense_parts[2])
        logging.error("Invalid date format")
        await update.message.reply_text("Your date argument is invalid, please use %Y-%m-%d %H:%M:%S format")
        return

    if not user_data.get(user_id):
        user_data[user_id] = []
    expense = Expense(expense_category, expense_cost, date)
    user_data[user_id].append(expense)
    await update.message.reply_text(f"Your expense: {expense} add success")


async def list_expense(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if not user_data.get(user_id):
        await update.message.reply_text("Your dont have expense.")
        return
    result = "\n".join([f"{i + 1} {t}" for i, t in enumerate(user_data[user_id])])
    await update.message.reply_text(result)


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Command start was triggered")
    await update.message.reply_text(
        "Welcome to my Expense Bot!\n"
        "Commands: \n"
        "Added expense: /add expense cost (integer) date (Y-M-D h:m:s) \n"
    )


def run():
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("Application build successfully!")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("add", add_expense))
    app.add_handler(CommandHandler("list", list_expense))

    app.run_polling()


if __name__ == '__main__':
    run()
