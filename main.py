import os
import datetime
import locale
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


def speakrs_menu(update, _):
    query = update.callback_query
    query.answer()
    programs_names = []
    for name_program in bot_db_program:
        programs_names.append(name_program[1])
    keyboard = [InlineKeyboardButton('Назад', callback_data=str(TWO))]
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "Здравствуйте. Это официальный бот по поддержке участников 🤖."
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST

def open_description(update, _):
    query = update.callback_query
    query.answer()
    keyboard = [InlineKeyboardButton('Назад', callback_data=str(TWO))]
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "Здравствуйте. Это официальный бот по поддержке участников 🤖."
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST

def open_program(update, _):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton('Назад', callback_data=str(ONE))]]
    programs_names = []
    for name_program in bot_db_program:
        programs_names.append(name_program[1])
    for program_name in set(programs_names):
        keyboard.append([InlineKeyboardButton(program_name, callback_data=str(program_name))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "Здравствуйте. Это официальный бот по поддержке участников 🤖."
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST


def open_opening_events(update, _):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton('Назад', callback_data=str(TWO))]]
    descriptions = []
    programs_names = []
    for name_program in bot_db_program:
        if str(query.data) == str(name_program[1]):
            programs_names.append(name_program[2])
    for description in bot_db_program:
        descriptions.append([description[2], description[3]])
    for program_name in set(programs_names):
        keyboard.append([InlineKeyboardButton(program_name, callback_data=str(THREE))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    theme_text = "Здравствуйте. Это официальный бот по поддержке участников 🤖."
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    return FIRST

def output_db():
    with sqlite3.connect('db2.sqlite3') as db:
        cur = db.cursor()
        for info in cur.execute("SELECT * FROM bot_db_program;"):
            bot_db_program.append(info)
        for info in cur.execute("SELECT * FROM bot_db_speaker;"):
            bot_db_speaker.append(info)
output_db()

def main():
    output_db()
    load_dotenv()
    tg_token = os.environ.get("TG_TOKEN")
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    programs_names = []
    speakers_programs_name = []
    descriptions = []
    second = []
    first = [
        CallbackQueryHandler(
            open_menu, pattern='^' + str(ONE) + '$'
        ),
        CallbackQueryHandler(
            open_program, pattern='^' + str(TWO) + '$'
        ),
        CallbackQueryHandler(
            open_description, pattern='^' + str(THREE) + '$'
        ),
        CallbackQueryHandler(
            speakrs_menu, pattern='^' + str(FOUR) + '$'
        )
    ]

    for name_program in bot_db_program:
        programs_names.append(name_program[1])
        descriptions.append(name_program[3])
    for speaker_name_program in bot_db_speaker:
        speakers_programs_name.append(speaker_name_program[3])
    speakers_programs_name = set(speakers_programs_name)
    programs_names = set(programs_names)
    for speaker_program_name in speakers_programs_name:
        first.append(CallbackQueryHandler(
            speakrs_menu, pattern='^' + str(speaker_program_name) + '$'
        ))
    for program_name in programs_names:
        first.append(CallbackQueryHandler(
            open_opening_events, pattern='^' + str(program_name) + '$'
        ))
    for description in descriptions:
        first.append(CallbackQueryHandler(
            open_description, pattern='^' + str(description) + '$'
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
