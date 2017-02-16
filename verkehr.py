import geopy.distance
import csv
import logging

hst = 'Helmholtz'
offset = 0
count = 5

logging.basicConfig(level=logging.DEBUG)

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
    print(reply_keyboard)
