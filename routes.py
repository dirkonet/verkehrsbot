"""
Routes and views for the bottle application.
"""

from bottle import route, request, view, run
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import dvb
import csv
import geopy.distance
import os, datetime

import sys
sys.stderr = open('D:\\home\\LogFiles\\stderr.txt', 'w')

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
    try:
        with open('allstations.csv', newline='') as infile:
            csv_reader = csv.reader(infile, delimiter=';')
            stations = [(int(row[0]), float(row[2]), float(row[1]), row[3]) for row in csv_reader]

            log('Received location lat {}, lon {}'.format(update.message.location.latitude, update.message.location.longitude))
            coord = (float(update.message.location.latitude), float(update.message.location.longitude))
            log('Read {} stations and coord {}'.format(len(stations), coord))
            pts = [geopy.Point(p[1], p[2], p[0]) for p in stations]
            log('Read {} points, first is {}'.format(len(pts), pts[0]))
            sts = [p[3] for p in stations]
            log('Read {} station names, first is {}'.format(len(sts), sts[0]))
            onept = geopy.Point(coord[0], coord[1])
            log('onept: {}'.format(onept))
            alldist = [(p, geopy.distance.distance(p, onept).m) for p in pts]
            log('Calculated {} distances'.format(len(alldist)))
            nearest_point = min(alldist, key=lambda x: (x[1]))[0]
            log('Nearest point id: {}'.format(sts[int(nearest_point.altitude)]))
            msg = 'Nächstgelegene Station: {} in {:.0f}m'.format(sts[int(nearest_point.altitude)], min(alldist, key=lambda x: (x[1]))[1])
            log(msg)
            bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text=str(e))


def log(txt):
    """Logs fatal errors to a log file if WSGI_LOG env var is defined"""
    log_file = os.environ.get('WSGI_LOG')
    if log_file:
        f = open(log_file, 'a+')
        try:
            f.write('%s: %s\n' % (datetime.datetime.now(), txt))
        finally:
            f.close()