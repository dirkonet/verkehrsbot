"""
Routes and views for the bottle application.
"""

from bottle import route, request, view, run
import telegram
from telegram.ext import Dispatcher, CommandHandler

BOT_TOKEN='311882778:AAGrL6E3zf7wFySOzD5gFGm2HFGIDY_hdK8'
APP_NAME='verkehrsbot'


@route('/')
def home():
    """Renders the home page."""
    return 'Nothing to see here, move along.'


@route('/setHook')
def set_hook():
    """Sets the bot's web hook address"""
    bot = telegram.Bot(BOT_TOKEN)
    result = bot.setWebhook(webhook_url='https://{}.azurewebsites.de/botHook'.format(APP_NAME))
    return str(result)


@route('/botHook', method='POST')
def bot_hook():
    bot = telegram.Bot(BOT_TOKEN)
    dispatcher = Dispatcher(bot, None, workers=0)
    update = telegram.update.Update.de_json(request.json, bot)

    dispatcher.add_handler(CommandHandler('Abfahrten', abfahrten, pass_args=True))

    #bot.sendMessage(chat_id=update.message.chat_id, text=reply(update.message.text, update.message.from_user.username))
    return 'OK'


def reply(text, username):
    return 'Hello {}, I got your message.'.format(username)


def abfahrten(bot, update, args):
    if len(args) < 1:
        update.message.reply_text = 'Bitte Haltestelle angeben.'
        return False

    hst = args[0]

    if len(args) < 2:
        minutes = 0
    else:
        minutes = args[1]

    update.message.reply_text = 'Abfahrten für {} in {} Minuten:'.format(hst, minutes)
    return True
