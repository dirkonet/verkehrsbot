"""
Routes and views for the bottle application.
"""

from bottle import route, request, view, run
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import dvb
import csv
import geopy.distance

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
    dispatcher.add_handler(CommandHandler('abfahrten', abfahrten, pass_args=True))
    dispatcher.add_handler(CommandHandler('Abfahrt', abfahrten, pass_args=True))
    dispatcher.add_handler(CommandHandler('abfahrt', abfahrten, pass_args=True))
    dispatcher.add_handler(CommandHandler('A', abfahrten, pass_args=True))
    dispatcher.add_handler(CommandHandler('a', abfahrten, pass_args=True))
    dispatcher.add_handler(CommandHandler('Hilfe', hilfe))
    dispatcher.add_handler(MessageHandler(Filters.location, nearest_stations))
    update = telegram.update.Update.de_json(request.json, bot)
    dispatcher.process_update(update)

    return 'OK'


def abfahrten(bot, update, args):
    if len(args) < 1:
        bot.sendMessage(chat_id=update.message.chat_id, text='Bitte Haltestelle angeben.')
        return False

    if len(args) > 1:
        hst = args[:-1]
        offset = args[-1]

        if offset.isdigit():  # Offset is time in minutes
            offset = int(offset)
        elif ':' in offset:  # Offset is clock time, TODO
            offset = 1
        else:  # No offset given -> reappend
            hst.append(offset)
            offset = 0
    else:
        hst = args
        offset = 0

    hst = ' '.join(map(str, hst))
    message = get_abfahrten(hst, offset)

    bot.sendMessage(chat_id=update.message.chat_id, text=message)
    return True


def get_abfahrten(hst, offset):
    results = dvb.monitor(hst, offset, 5)
    message = 'Abfahrten für {}'.format(hst)
    if offset != 0:
        message += ' in {} Minuten:'.format(offset)
    else:
        message += ':'

    if len(results) < 1 and ' ' in hst and 'Dresden' not in hst:
        hstsplit = hst.split(' ')
        results = dvb.monitor(' '.join(hstsplit[1:]), offset, 5, hstsplit[0])
        message += '\n({} wurde als Ort interpretiert)'.format(hstsplit[0])

    for r in results:
        message += '\n{} {} - {} min'.format(r['line'], r['direction'], r['arrival'])

    return message


def nearest_stations(bot, update, count=5):
    # http://stackoverflow.com/a/28368926
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
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode='HTML',
                        reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def hilfe(bot, update):
    message = 'Der Bot zeigt die Abfahrten im VVO-Gebiet an. Mit "/Abfahrten Haltestelle" werden die nächsten Abfahrten' \
              'angezeigt, mit "/Abfahrten Haltestelle 5" die in fünf Minuten. Sendet man dem Bot den aktuellen Standort,' \
              'werden die fünf nächstgelegenen Haltestellen mit Entfernung und Link zu Google Maps angezeigt.\n' \
              'Basierend auf dvbpy und python-telegram-bot.'
    bot.sendMessage(chat_id=update.message.chat_id, text=message)
