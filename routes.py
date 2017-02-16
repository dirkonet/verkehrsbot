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
    dispatcher.add_handler(MessageHandler(Filters.location, nearest_stations))
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

    try:
        if len(args) > 1:
            hst = args[:-1]
            offset = args[-1]

            if offset.isdigit():  # Offset is time in minutes
                offset = int(offset)
            elif ':' in offset:   # Offset is clock time, TODO
                offset = 1
            else:                 # No offset given -> reappend
                hst.append(offset)
                offset = 0
        else:
            hst = args
            offset = 0

        hst = ' '.join(map(str, hst))
        message = get_abfahrten(hst, offset)
    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text='Huch: {}'.format(str(e)))

    bot.sendMessage(chat_id=update.message.chat_id, text=message)
    return True


def get_abfahrten(hst, offset):
    results = dvb.monitor(hst, offset, 5)

    message = 'Abfahrten für {}'.format(hst)
    if offset != 0:
        message += ' in {} Minuten:'.format(offset)
    else:
        message += ':'

    for r in results:
        message += '\n{} - {} - {}'.format(r['line'], r['direction'], r['arrival'])

    return message


def nearest_stations(bot, update, count=5):
    with open('allstations.csv', newline='', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile, delimiter=';')
        stations = [(int(row[0]), float(row[1]), float(row[2]), row[3]) for row in csv_reader]

        coord = (float(update.message.location.latitude), float(update.message.location.longitude))
        pts = [geopy.Point(p[1], p[2], p[0]) for p in stations]
        sts = [p[3] for p in stations]
        onept = geopy.Point(coord[0], coord[1])
        alldist = [(p, geopy.distance.distance(p, onept).m) for p in pts]
        nearest = sorted(alldist, key=lambda x: (x[1]))[:count]
        nearest_points = [n[0] for n in nearest]
        nearest_distances = [n[1] for n in nearest]
        nearest_sts = [sts[int(n.altitude)] for n in nearest_points]
        msg = 'Nächstgelegene Stationen:'
        for s, d, p in zip(nearest_sts, nearest_distances, nearest_points):
            msg += '\n{} (<a href="https://www.google.de/maps?q={},{}">{:.0f}m</a>)'.format(s, p.latitude, p.longitude, d)

        reply_keyboard = [[telegram.KeyboardButton(text='/Abfahrten {}'.format(n))] for n in nearest_sts]
        #    nearest_st, nearest_distance, nearest_point.latitude, nearest_point.longitude)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode='HTML',
                        reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def nearest_station(bot, update):
    # http://stackoverflow.com/a/28368926
    with open('allstations.csv', newline='', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile, delimiter=';')
        stations = [(int(row[0]), float(row[1]), float(row[2]), row[3]) for row in csv_reader]

        coord = (float(update.message.location.latitude), float(update.message.location.longitude))
        pts = [geopy.Point(p[1], p[2], p[0]) for p in stations]
        sts = [p[3] for p in stations]
        onept = geopy.Point(coord[0], coord[1])
        alldist = [(p, geopy.distance.distance(p, onept).m) for p in pts]
        nearest = min(alldist, key=lambda x: (x[1]))
        nearest_point = nearest[0]
        nearest_distance = nearest[1]
        nearest_st = sts[int(nearest_point.altitude)]
        msg = 'Nächstgelegene Station: {} in {:.0f}m (<a href="https://www.google.de/maps?q={},{}">Google Maps</a>)'.format(nearest_st, nearest_distance, nearest_point.latitude, nearest_point.longitude)
        msg += '\n'
        msg += get_abfahrten(nearest_st, 0)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode='HTML')
