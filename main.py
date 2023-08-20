import logging
import json
from json.decoder import JSONDecodeError

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler
from datetime import datetime, timedelta

category_expense = ['food', 'car', 'house', 'living', 'travel', 'extra', 'medicine']
TOKEN_BOT = '6562178126:AAFnLXiXgGj9D2cClMm1akj0Ej5M8Td7t7w'
try:
    with open('user_expense.json', 'r') as f:
        user_expense = json.loads(f.read())
except (JSONDecodeError, FileNotFoundError):
    user_expense = dict()

try:
    with open('user_income.json', 'r') as f:
        user_income = json.loads(f.read())
except (JSONDecodeError, FileNotFoundError):
    user_income = dict()

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
        return f"{self.category} {self.cost} {self.date.strftime('%Y-%m-%d %H:%M')}"


class Income:
    def __init__(self, category: str, cost: int, date: datetime):
        self.category = category
        self.cost = cost
        self.date = date

    def __str__(self):
        return f"{self.category} {self.cost} {self.date.strftime('%Y-%m-%d %H:%M')}"


async def add_expense(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    expense_parts = ' '.join(context.args).split()
    try:
        expense_category = expense_parts[0]
        date_expense = " ".join(expense_parts[2:])
    except IndexError:
        await update.message.reply_text("You entered incorrect command")
        return
    if expense_category not in category_expense:
        await update.message.reply_text("You entered incorrect category for expense, please check with:\n "
                                        "['food', 'car', 'house', 'living', 'travel', 'extra', 'medicine']")
        return

    try:
        expense_cost = int(expense_parts[1].strip())
    except ValueError:
        logging.error("Invalid cost error")
        await update.message.reply_text("Your cost argument is invalid, please enter integer num")
        return

    try:
        date = datetime.strptime(date_expense.strip(), '%Y-%m-%d %H:%M')
    except ValueError:
        logging.error("Invalid date format")
        await update.message.reply_text("Your date argument is invalid, please use %Y-%m-%d %H:%M format")
        return

    if not user_expense.get(user_id):
        user_expense[user_id] = []
    expense = Expense(expense_category, expense_cost, date)
    user_expense[user_id].append(str(expense))
    to_json = json.dumps(user_expense, indent=4)
    with open('user_expense.json', 'w') as f:
        f.write(to_json)
    await update.message.reply_text(f"Your expense: {expense} add success")


async def list_expense(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_expense.get(user_id):
        await update.message.reply_text("Your dont have expense.")
        return
    sum_expense = sum(int(i.split()[1]) for i in user_expense[user_id])
    result = "\n".join([f"{i + 1} {t}" for i, t in enumerate(user_expense[user_id])])
    await update.message.reply_text(f"{result}\nSum of expense: {sum_expense}")


async def remove_expense(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_expense.get(user_id):
        await update.message.reply_text("You dont have any expense to remove")
        return

    try:
        remove_idx = int(context.args[0]) - 1
        expense = user_expense[user_id].pop(remove_idx)
        await update.message.reply_text(f"Expense {expense} removed success")
        with open('user_expense.json', 'w') as f:
            f.write(json.dumps(user_expense))
    except (ValueError, IndexError):
        await update.message.reply_text("Your entered invalid index")


async def list_expense_in_period(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_expense.get(user_id):
        await update.message.reply_text("You dont have any expense")
        return
    try:
        days = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text("You entered incorrect num days")
        return

    now = datetime.now()
    sum_expense = 0
    expense_period = []
    for expense in user_expense[user_id]:
        expense_list = expense.split()
        date = datetime.strptime(" ".join(expense_list[2:]), '%Y-%m-%d %H:%M')
        if date >= (now - timedelta(days=days)):
            expense_period.append(expense)
            sum_expense += int(expense_list[1])

    if expense_period:
        expense_info = '\n'.join([f"{i + 1} {t}" for i, t in enumerate(map(str, expense_period))])
        await update.message.reply_text(
            f"You Expense of {days} days:\n{expense_info}\nSum of the period: {sum_expense}")
    else:
        await update.message.reply_text(f"You don't have any expense of period {days} days")


async def add_income(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    income_parts = ' '.join(context.args).split()
    try:
        income_category = income_parts[0]
        income_date = " ".join(income_parts[2:])
    except IndexError:
        await update.message.reply_text("You entered incorrect command.")
        return

    try:
        income_cost = int(income_parts[1].strip())
    except ValueError:
        logging.error("Invalid cost error")
        await update.message.reply_text("Your cost argument is invalid, please enter integer num")
        return
    try:
        date = datetime.strptime(income_date.strip(), '%Y-%m-%d %H:%M')
    except ValueError:
        logging.error("Invalid date format")
        await update.message.reply_text("Your date argument is invalid, please use %Y-%m-%d %H:%M format")
        return

    if not user_income.get(user_id):
        user_income[user_id] = []
    income = Income(income_category, income_cost, date)
    user_income[user_id].append(str(income))
    with open('user_income.json', 'w') as f:
        f.write(json.dumps(user_income))
    await update.message.reply_text(f"Your expense: {income} add success")


async def remove_income(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_income.get(user_id):
        await update.message.reply_text("You dont have any income to remove")
        return

    try:
        income_idx = int(context.args[0]) - 1
        income = user_income[user_id].pop(income_idx)
        await update.message.reply_text(f"You income {income} removed success")
        with open('user_income.json', 'w') as f:
            f.write(json.dumps(user_income))
    except (ValueError, IndexError):
        await update.message.reply_text("You entered invalid index")


async def list_income(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_income.get(user_id):
        await update.message.reply_text("You dont have any income")
        return

    result = "\n".join([f"{i + 1} {t}" for i, t in enumerate(user_income[user_id])])
    sum_income = sum(int(i.split()[1]) for i in user_income[user_id])
    await update.message.reply_text(f"{result}\nSum income: {sum_income}")


async def list_income_in_period(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_income.get(user_id):
        await update.message.reply_text("You dont have any income")
        return
    try:
        days = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text("You entered incorrect num days")
        return

    now = datetime.now()
    sum_income = 0
    income_period = []
    for income in user_income[user_id]:
        income_list = income.split()
        if datetime.strptime(" ".join(income_list[2:]), '%Y-%m-%d %H:%M') >= (now - timedelta(days=days)):
            income_period.append(income)
            sum_income += int(income_list[1])

    if income_period:
        income_info = '\n'.join(map(str, income_period))
        await update.message.reply_text(
            f"You income of {days} days:\n{income_info}\nSum of the period: {sum_income}")
    else:
        await update.message.reply_text(f"You don't have any income of period {days} days")


async def static(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_income.get(user_id) and not user_expense.get(user_id):
        await update.message.reply_text("You dont have any expense and income")
        return
    if not user_expense.get(user_id):
        await update.message.reply_text("You dont have any expense")
    else:
        try:
            days = int(context.args[0])
        except (ValueError, IndexError):
            await update.message.reply_text("You entered incorrect num days")
            return

        now = datetime.now()
        sum_expense = 0
        expense_period = []
        for expense in user_expense[user_id]:
            expense_list = expense.split()
            if datetime.strptime(" ".join(expense_list[2:]), '%Y-%m-%d %H:%M') >= (now - timedelta(days=days)):
                expense_period.append(expense)
                sum_expense += int(expense_list[1])

        if expense_period:
            result_reply = ''
            for category in category_expense:
                if category in str(expense_period):
                    sum_expense_in_category = 0
                    result_reply += f'\nExpense in category {category}:\n'
                    for expense in expense_period:
                        if expense.split()[0] == category:
                            result_reply += f'{" ".join(expense.split()[1:])}\n'
                            sum_expense_in_category += int(expense.split()[1])
                    result_reply += f'Sum expense in category: {sum_expense_in_category}\n'
            await update.message.reply_text(f"{result_reply}\nSum Expense = {sum_expense}")
        else:
            await update.message.reply_text(f"You don't have any expense of period {days} days")
    await list_income_in_period(update, context)


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Command start was triggered")
    await update.message.reply_text(
        "Welcome to my Expense Bot!\n"
        "Commands: \n"
        "Added expense: /add_expense category (food, car, living, travel, extra, medicine) "
        "cost (integer) date (Y-M-D h:m) \n"
        "List expense: /list_expense \n"
        "Remove expense: /remove_expense № \n"
        "Expense of period: /expense_of_period days \n"
        "Add income: /add_income \n"
        "List income: /list_income \n"
        "Remove income: /remove_income № \n"
        "Income of period: /income_of_period days \n"
        "Static in period: /static days \n"

    )


def run():
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("Application build successfully!")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("add_expense", add_expense))
    app.add_handler(CommandHandler("list_expense", list_expense))
    app.add_handler(CommandHandler("remove_expense", remove_expense))
    app.add_handler(CommandHandler("expense_in_period", list_expense_in_period))
    app.add_handler(CommandHandler("add_income", add_income))
    app.add_handler(CommandHandler("remove_income", remove_income))
    app.add_handler(CommandHandler("list_income", list_income))
    app.add_handler(CommandHandler("income_in_period", list_income_in_period))
    app.add_handler(CommandHandler("static", static))

    app.run_polling()


if __name__ == '__main__':
    run()
