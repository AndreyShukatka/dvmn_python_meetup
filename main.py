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

locale.setlocale(locale.LC_ALL, "ru")
tg_token = os.environ.get("TG_TOKEN")

speakers = []
speakers_id = []
load_dotenv()
tg_token = os.environ.get("TG_TOKEN")

# Этапы/состояния разговора
FIRST, SECOND = range(2)
# Данные обратного вызова
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN = range(7)


def main_handler(update, context):
    chat_id = update.message.chat.id
    message = update.message.text
    bot = telegram.Bot(token=tg_token)
    for speaker in speakers:
        if speaker[-1] == 1:
            speaker_id = speaker[1]
            speaker_name = speaker[2]

    if str(speaker_id) != str(chat_id):
        keyboard = [[InlineKeyboardButton("Ответить", callback_data=str(FOUR))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=speaker_id, text=update.message.text, reply_markup=reply_markup)
        bot.send_message(chat_id=chat_id, text=f'Ваше сообщение отправлено для спикера:"{speaker_name}"')
    with sqlite3.connect('db.sqlite3') as db:
        cur = db.cursor()
        cur.execute(
            'INSERT INTO Chat (chat_id, message, id_speaker) VALUES (?, ?, ?)',
            (chat_id, message, speaker_id)
            )
        db.commit()
    return FIRST

def reply_user(update, _):
    query = update.callback_query
    query.answer()
    bot = telegram.Bot(token=tg_token)
    bot.send_message(chat_id=query.message.chat.id, text=input())
    print(query)



def create_speakers_list(speakers, speakers_id):

    with sqlite3.connect('db.sqlite3') as db:
        cur = db.cursor()
    for info in cur.execute("SELECT * FROM bot_db_speaker;"):
        speakers.append(info)
    for info in speakers:
        speakers_id.append(info[1])



def create_date(info):
    start_time = datetime.datetime.strptime(
        info[4], "%Y-%m-%d %H:%M:%S"
        ).strftime('%d %b %H:%M')
    finish_date = datetime.datetime.strptime(
        info[5], "%Y-%m-%d %H:%M:%S"
        ).strftime('%d %b %H:%M')
    return start_time, finish_date


def start_report(update, _):
    speaker_id = update.callback_query.message.chat.id
    query = update.callback_query
    query.answer()
    time = datetime.datetime.now()
    keyboard = [
        [InlineKeyboardButton("Закончить доклад", callback_data=str(SEVEN))],
        [InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
         InlineKeyboardButton("Меню", callback_data=str(ONE))],
        ]
    theme_text = f"Доклад начался в {time.strftime('%H:%M:%S %Y-%m-%d')}"
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    with sqlite3.connect('db.sqlite3') as db:
        cur = db.cursor()
        sql_update_query = f"Update bot_db_speaker set recording_progress = 1 where telegram_id = {speaker_id}"
        sql_stop_report = f'Update bot_db_speaker set time_start = "{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" where telegram_id = {speaker_id}'
        cur.execute(sql_update_query)
        cur.execute(sql_stop_report)
    return FIRST


def stop_report(update, _):
    speaker_id = update.callback_query.message.chat.id
    query = update.callback_query
    query.answer()
    time = datetime.datetime.now()
    keyboard = [
        [InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
         InlineKeyboardButton("Меню", callback_data=str(ONE))],
    ]
    theme_text = f"Доклад закончился в {time.strftime('%H:%M:%S %Y-%m-%d')}"
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=theme_text, reply_markup=reply_markup
    )
    with sqlite3.connect('db.sqlite3') as db:
        cur = db.cursor()
        sql_update_query = f"Update bot_db_speaker set recording_progress = '' where telegram_id = {speaker_id}"
        sql_stop_report = f'Update bot_db_speaker set time_stop = "{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" where telegram_id = {speaker_id}'
        cur.execute(sql_update_query)
        cur.execute(sql_stop_report)
    return FIRST


def add_text_speaker():
    all_text = f'С докладом сегодня выступает:\n'
    n = 1
    for info in speakers:
        create_date(info)
        info_text = f'Спикер №{n} {info[2]}\n'\
                    f'-Тема"{info[3]}"\n'\
                    f'-Начало вещяния {create_date(info)[0]}\n'\
                    f'-Конец вещяния {create_date(info)[1]}\n'
        all_text = all_text + info_text
        n += 1
    return all_text


def send_message_for_speaker(update, context):
    for speaker in speakers:
        if speaker[-1] == 1:
            chat_id = speaker[1]
    query = update.callback_query
    query.answer()
    keyboard = [
            [InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
            InlineKeyboardButton("Меню", callback_data=str(ONE))]
    ]
    for info in speakers:
        if info[1]+'send_message_for_speaker' == query.data:
            theme_text = f"Напишите Ваш вопрос для докладчика {info[2]}"
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text=theme_text, reply_markup=reply_markup
            )

    return FIRST


def theme_spiker(update, _):
    speakers.clear()
    create_speakers_list(speakers, speakers_id)
    query = update.callback_query
    query.answer()
    for info in speakers:
        if info[1]+'open_speakers' == query.data:
            theme_text = f'Выбран {info[2]}\nТема доклада "{info[3]}"\n' \
                         f'Начало выступления {create_date(info)[0]}\n' \
                         f"Окончаниеи выступления {create_date(info)[1]}"
            keyboard = [
                    [InlineKeyboardButton(
                        "Задать вопрос",
                        callback_data=str(info[1]+'send_message_for_speaker')
                    )],
                    [InlineKeyboardButton(
                        "Докладчики", callback_data=str(TWO)
                    ),
                    InlineKeyboardButton("Меню", callback_data=str(ONE))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
            text=theme_text, reply_markup=reply_markup
            )
    return FIRST


def start(update, _):
    superuser = False
    for speaker_id in speakers_id:
        if str(update.message.chat.id) == str(speaker_id):
            superuser = True
    if superuser == False:
        """Вызывается по команде `/start`."""
        # Создаем `InlineKeyboard`, где каждая кнопка имеет
        # отображаемый текст и строку `callback_data`
        # Клавиатура - это список строк кнопок, где каждая строка,
        # в свою очередь, является списком `[[...]]`
        keyboard = [
            [
                InlineKeyboardButton("Меню", callback_data=str(ONE)),
                InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
                InlineKeyboardButton("F.A.Q", callback_data=str(THREE))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Отправляем сообщение с текстом и добавленной клавиатурой `reply_markup`
        update.message.reply_text(
            text="Добро пожаловать на нашей встрече", reply_markup=reply_markup
        )
        # Сообщаем `ConversationHandler`, что сейчас состояние `FIRST`
        return FIRST
    else:
        keyboard = [
            [InlineKeyboardButton("Начать доклад", callback_data=str(SIX))],
            [
                InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
                InlineKeyboardButton("F.A.Q", callback_data=str(THREE))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Отправляем сообщение с текстом и добавленной клавиатурой `reply_markup`
        update.message.reply_text(
            text="Добро пожаловать на нашей встрече", reply_markup=reply_markup
        )
        # Сообщаем `ConversationHandler`, что сейчас состояние `FIRST`
        return FIRST

def open_menu(update, _):
    """Показ нового выбора кнопок"""
    query = update.callback_query
    query.answer()
    superuser = False
    for speaker_id in speakers_id:
        if str(update.callback_query.message.chat.id) == str(speaker_id):
            superuser = True
    if superuser == False:
        """Вызывается по команде `/start`."""
        # Создаем `InlineKeyboard`, где каждая кнопка имеет
        # отображаемый текст и строку `callback_data`
        # Клавиатура - это список строк кнопок, где каждая строка,
        # в свою очередь, является списком `[[...]]`
        keyboard = [
            [
                InlineKeyboardButton("Меню", callback_data=str(ONE)),
                InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
                InlineKeyboardButton("F.A.Q", callback_data=str(THREE))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        theme_text = "Тут из базы повестка нашей встречи"
        query.edit_message_text(
            text=theme_text, reply_markup=reply_markup
        )
        return FIRST
    else:
        keyboard = [
            [InlineKeyboardButton("Начать доклад", callback_data=str(SIX))],
            [InlineKeyboardButton("Закончить доклад", callback_data=str(SEVEN))],
            [
                InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
                InlineKeyboardButton("F.A.Q", callback_data=str(THREE))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        theme_text = "Тут из базы повестка нашей встречи"
        query.edit_message_text(
            text=theme_text, reply_markup=reply_markup
        )
        return FIRST


def open_speakers(update, _):
    """Показ нового выбора кнопок"""
    speakers.clear()
    create_speakers_list(speakers, speakers_id)
    query = update.callback_query
    query.answer()
    keyboard_speaker = []
    for name in speakers:
        keyboard_speaker.append([InlineKeyboardButton(
            name[2], callback_data=str(name[1] + 'open_speakers'))
        ])
    keyboard_menu = [
            [InlineKeyboardButton("Меню", callback_data=str(ONE)),
            InlineKeyboardButton("F.A.Q", callback_data=str(THREE))]
        ]
    keyboard_total = keyboard_speaker + keyboard_menu
    reply_markup = InlineKeyboardMarkup(keyboard_total)
    query.edit_message_text(
        text=add_text_speaker(), reply_markup=reply_markup
    )
    return FIRST


def open_faq(update, _):
    """Показ нового выбора кнопок"""
    speakers.clear()
    create_speakers_list(speakers, speakers_id)
    for speaker in speakers:
        if speaker[-1] == 1:
            text = f'В данный момент выступает спикер {speaker[2]}'
            speaker_name = speaker[2]
            speaker_id = speaker[1] + 'open_speakers'
            keyboard = [[InlineKeyboardButton(speaker_name, callback_data=str(speaker_id))],
                        [
                            InlineKeyboardButton("Меню", callback_data=str(ONE)),
                            InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
                        ]
                        ]
        else:
            text = 'На данный момент никто не выступает'
            query = update.callback_query
            query.answer()
            keyboard = [
                    [
                    InlineKeyboardButton("Меню", callback_data=str(ONE)),
                    InlineKeyboardButton("Докладчики", callback_data=str(TWO)),
                ]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return FIRST


def main():
    add_text_speaker()
    load_dotenv()
    tg_token = os.environ.get("TG_TOKEN")
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    create_speakers_list(speakers, speakers_id)
    second = []
    first = [
                CallbackQueryHandler(
                    open_menu, pattern='^' + str(ONE) + '$'
                ),
                CallbackQueryHandler(
                    open_speakers, pattern='^' + str(TWO) + '$'
                ),
                CallbackQueryHandler(
                    open_faq, pattern='^' + str(THREE) + '$'
                ),
                CallbackQueryHandler(
                    send_message_for_speaker, pattern='^' + str(FIVE) + '$'
                ),
                CallbackQueryHandler(
                    start_report, pattern='^' + str(SIX) + '$'
                ),
                CallbackQueryHandler(
                    stop_report, pattern='^' + str(SEVEN) + '$'
                ),
                CallbackQueryHandler(
                    reply_user, pattern='^' + str(FOUR) + '$'
                )
                ]
    for info_speaker in speakers:
        first.append(CallbackQueryHandler(
            theme_spiker, pattern='^' + str(info_speaker[1] + 'open_speakers') + '$'
        ))
        first.append(CallbackQueryHandler(
            send_message_for_speaker,
            pattern='^' + str(info_speaker[1] + 'send_message_for_speaker') + '$')
        )


    # Настройка обработчика разговоров с состояниями `FIRST` и `SECOND`
    # Используем параметр `pattern` для передачи `CallbackQueries` с
    # определенным шаблоном данных соответствующим обработчикам
    # ^ - означает "начало строки"
    # $ - означает "конец строки"
    # Таким образом, паттерн `^ABC$` будет ловить только 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={  # словарь состояний разговора, возвращаемых callback функциями
            FIRST: first,
            SECOND: second
        },
        fallbacks=[CommandHandler('start', start)],
    )
    # Добавляем `ConversationHandler` в диспетчер, который
    # будет использоваться для обработки обновлений
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(
        telegram.ext.MessageHandler(telegram.ext.Filters.text, main_handler)
    )
    updater.dispatcher.add_handler(
        telegram.ext.MessageHandler(telegram.ext.Filters.text, reply_user)
    )
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
