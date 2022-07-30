import os
import json
import datetime
import locale
from utils import db_to_json, db_to_json_dic
import sqlite3
import telegram
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

FIRST, SECOND = range(2)
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN = range(7)
bot_db_program = []
bot_db_speaker = []


def start(update, _):
    query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton("Меню", callback_data=str(ONE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text="Здравствуйте. Это официальный бот по поддержке участников 🤖.", reply_markup=reply_markup
    )
    return FIRST


def open_menu(update, _):
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("📋Программа", callback_data=str(TWO)),
            InlineKeyboardButton("🗣Задать вопрос спикеру", callback_data=str(FOUR))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "Здравствуйте. Это официальный бот по поддержке участников 🤖."
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST


def open_description(update, _):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton('Назад', callback_data=str(query.data))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "oppa"
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST

def open_program(update, _):
    sql_query = "SELECT DISTINCT top_block FROM bot_db_program"
    formatted = db_to_json(sql_query)
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton('Назад', callback_data=str(ONE))]
    ]
    for item in formatted:
        keyboard.append([InlineKeyboardButton(item, callback_data=str(item))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "Здравствуйте. Это официальный бот по поддержке участников 🤖."
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST


def open_opening_events(update, _):
    query = update.callback_query
    print(query.data)
    sql_query = f'SELECT id, bottom_block FROM bot_db_program WHERE top_block = \'{query.data}\''
    formatted = db_to_json_dic(sql_query)
    query.answer()
    keyboard = [[InlineKeyboardButton('Назад', callback_data=str(TWO))]]
    for info in formatted:
        keyboard.append([InlineKeyboardButton(info[1], callback_data=str(info[0]) +'event')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "Здравствуйте. Это официальный бот по поддержке участников 🤖."
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST


def main():
    load_dotenv()
    tg_token = os.environ.get("TG_TOKEN")
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    second = []
    first = [
        CallbackQueryHandler(
            open_menu, pattern='^' + str(ONE) + '$'
        ),
        CallbackQueryHandler(
            open_program, pattern='^' + str(TWO) + '$'
        ),
        CallbackQueryHandler(
            open_description, pattern='^' + str(THREE) + '$')

    ]
    sql_query = "SELECT DISTINCT top_block FROM bot_db_program"
    formatted = db_to_json(sql_query)
    for item in formatted:
        first.append(CallbackQueryHandler(
            open_opening_events, pattern= '^' + str(item) + '$'
        ))
    sql_query = "SELECT DISTINCT id FROM bot_db_program"
    id = db_to_json_dic(sql_query)
    for number in id:
        first.append(CallbackQueryHandler(
            open_description, pattern= '^' + str(number) + 'event' + '$'
        ))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: first,
            SECOND: second
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
