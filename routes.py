"""
Routes and views for the bottle application.
"""

from bottle import route, request, view, run
import telegram

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
    update = telegram.update.Update.de_json(request.json, bot)
    bot.sendMessage(chat_id=update.message.chat_id, text=get_data(update.message.text, update.message.from_user.username))
    return 'OK'


def get_data(text, username):
    return 'Hello, {}'.format(username)
