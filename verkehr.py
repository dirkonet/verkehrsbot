#encoding: utf-8
import dvb
import geopy
import geopy.distance
import csv
import logging

hst = 'Helmholtz'
offset = 0
#results = dvb.monitor(hst, offset, 5, 'Dresden')

logging.basicConfig(level=logging.DEBUG)

#message = 'Abfahrten für {} in {} Minuten:'.format(hst, offset)

#for r in results:
#    message += '\n{} - {} - {}'.format(r['line'], r['direction'], r['arrival'])

# http://stackoverflow.com/a/28368926
# with open('allstations.csv', newline='') as infile:
#     csv_reader = csv.reader(infile, delimiter=';')
#     stations = [(int(row[0]), float(row[1]), float(row[2]), row[3]) for row in csv_reader]
#     coord = (13.700551,51.040385)
#     logging.debug('Received location lat {}, lon {}'.format(coord[1], coord[0]))
#     pts = [geopy.Point(p[1], p[2], p[0]) for p in stations]
#     sts = [p[3] for p in stations]
#     onept = geopy.Point(coord[0], coord[1])
#     alldist = [(p, geopy.distance.distance(p, onept).m) for p in pts]
#     nearest_point = min(alldist, key=lambda x: (x[1]))[0]
#     print('Nächstgelegene Station: {} in {:.0f}m'.format(sts[int(nearest_point.altitude)], min(alldist, key=lambda x: (x[1]))[1]))

count = 5

with open('allstations.csv', newline='', encoding='utf-8') as infile:
    csv_reader = csv.reader(infile, delimiter=';')
    stations = [(int(row[0]), float(row[1]), float(row[2]), row[3]) for row in csv_reader]

    coord = (51.025654, 13.723377)
    pts = [geopy.Point(p[1], p[2], p[0]) for p in stations]
    sts = [p[3] for p in stations]
    onept = geopy.Point(coord[0], coord[1])
    alldist = [(p, geopy.distance.distance(p, onept).m) for p in pts]
    nearest = sorted(alldist, key=lambda x: (x[1]))[:count]
    nearest_points = [n[0] for n in nearest]
    nearest_distances = [n[1] for n in nearest]
    nearest_sts = [sts[int(n.altitude)] for n in nearest_points]
    msg = 'Nächstgelegene Stationen:\n'

    reply_keyboard = ['/Abfahrten {}'.format(n) for n in nearest_sts]
    #    nearest_st, nearest_distance, nearest_point.latitude, nearest_point.longitude)
    print(reply_keyboard)
