"""
Routes and views for the bottle application.
"""

from bottle import route, request, view, run
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import dvb
import csv
import geopy
import logging

BOT_TOKEN='311882778:AAGrL6E3zf7wFySOzD5gFGm2HFGIDY_hdK8'
APP_NAME='verkehrsbot'
logging.basicConfig(level=logging.DEBUG)

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
    dispatcher.add_handler(CommandHandler('Abfahrten', abfahrten, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.location, nearest_station))
    update = telegram.update.Update.de_json(request.json, bot)
    dispatcher.process_update(update)

    #bot.sendMessage(chat_id=update.message.chat_id, text=reply(update.message.text, update.message.from_user.username))
    return 'OK'


def reply(text, username):
    return 'Hello {}, I got your message.'.format(username)


def abfahrten(bot, update, args):
    if len(args) < 1:
        bot.sendMessage(chat_id=update.message.chat_id, text='Bitte Haltestelle angeben.')
        return False

    hst = args[0]

    if len(args) < 2:
        offset = 0
    else:
        offset = args[1]

    results = dvb.monitor(hst, offset, 5, 'Dresden')

    message = 'Abfahrten für {} in {} Minuten:'.format(hst, offset)

    for r in results:
        message += '\n{} - {} - {}'.format(r['line'], r['direction'], r['arrival'])

    bot.sendMessage(chat_id=update.message.chat_id, text=message)
    return True

def nearest_station(bot, update):
    # http://stackoverflow.com/a/28368926
    with open('allstations.csv', newline='') as infile:
        csv_reader = csv.reader(infile, delimiter=';')
        stations = [(int(row[0]), float(row[1]), float(row[2]), row[3]) for row in csv_reader]

        logging.debug('Received location lat {}, lon {}'.format(update.message.location.latitude, update.message.location.longitude))
        coord = (float(update.message.location.longitude), float(update.message.location.latitude))
        pts = [geopy.Point(p[1], p[2], p[0]) for p in stations]
        sts = [p[3] for p in stations]
        onept = geopy.Point(coord[0], coord[1])
        alldist = [(p, geopy.distance.distance(p, onept).m) for p in pts]
        nearest_point = min(alldist, key=lambda x: (x[1]))[0]
        bot.sendMessage(chat_id=update.message.chat_id, text='Nächstgelegene Station: {} in {:.0f}m'.format(sts[int(nearest_point.altitude)],
                                                             min(alldist, key=lambda x: (x[1]))[1]))

