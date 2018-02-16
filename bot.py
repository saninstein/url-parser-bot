from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler)
from utils import *
import logging


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = ''


WHITELIST = [
    'alex_deerk'
]

reply_keyboard = [['Show'],['Confirm', 'Delete']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def whitelist(handler):
    """ whitelist middleware """
    def _wrapper(*args, **kwargs):
        if args and len(args) > 1:
            msg = args[1].message
            if msg and msg.from_user and msg.from_user.username:
                if msg.from_user.username in WHITELIST:
                    return handler(*args, **kwargs)
            return None
    return _wrapper


def save(username, urls):
    # run when user confirm urls
    print(username, urls)


@whitelist
def start(bot, update):
    update.message.reply_text("Enter the urls", reply_markup=markup)


@whitelist
def add_data(bot, update, user_data):
    urls_set = set()

    text = update.message.text
    urls_set |= set(parse_urls(text))

    reply_to_message = update.message.reply_to_message
    if reply_to_message:
        urls_set |= set(parse_urls(reply_to_message.text))

    answer = "URLs:\n" + list_to_string(urls_set)

    if 'urls' in user_data:
        user_data['urls'] |= urls_set
    else:
        user_data['urls'] = urls_set

    update.message.reply_text(answer, reply_markup=markup)


@whitelist
def delete_data(bot, update, user_data):
    is_empty = True
    if 'urls' in user_data:
        is_empty = user_data.pop('urls', True)

    if is_empty:
        answer = "URLs list is empty"
    else:
        answer = "URLs removed"
    update.message.reply_text(answer, reply_markup=markup)


@whitelist
def show_data(bot, update, user_data):
    if 'urls' in user_data and len(user_data['urls']):
        answer = "URLs:\n" + list_to_string(user_data['urls'])
    else:
        answer = "URLs list is empty"
    update.message.reply_text(answer, reply_markup=markup)


@whitelist
def confirm_data(bot, update, user_data):
    urls = None
    if 'urls' in user_data:
        urls = user_data['urls']
        user_data.pop('urls', None)

    if urls:
        save(update.message.from_user, urls)
        answer = "Confirmed URLs:\n" + list_to_string(urls)
    else:
        answer = "URLs list is empty"
    update.message.reply_text(answer, reply_markup=markup)
    user_data.clear()


@whitelist
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    message_filter = Filters.text & (~ Filters.command)
    handlers = (
        CommandHandler('start', start),
        RegexHandler('^Show$', show_data, pass_user_data=True),
        RegexHandler('^Confirm$', confirm_data, pass_user_data=True),
        RegexHandler('^Delete$', delete_data, pass_user_data=True),
        MessageHandler(message_filter, add_data, pass_user_data=True),
    )

    for handler in handlers:
        dp.add_handler(handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()


