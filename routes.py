"""
Routes and views for the bottle application.
"""

from bottle import route, request
import telegram

TOKEN='311882778:AAGrL6E3zf7wFySOzD5gFGm2HFGIDY_hdK8'
APPNAME='verkehrsbot'


@route('/')
def home():
    """Renders the home page."""
    return 'Nothing to see here, move along.'


@route('/setHook')
def setHook():
    """Sets the bot's web hook address"""
    bot = telegram.Bot(TOKEN)
    botWebhookResult = bot.setWebhook(webhook_url='https://{}.azurewebsites.de/botHook'.format(APPNAME))
    return str(botWebhookResult)


@route('/botHook', method='POST')
def botHook():
    bot = telegram.Bot(TOKEN)
    update = telegram.update.Update.de_json(request.json, bot)
    bot.sendMessage(chat_id=update.message.chat_id, text=getData(update.message.text, update.message.from_user.username))
    return 'OK'


def getData(text, username):
    return 'Hello, {}'.format(username)