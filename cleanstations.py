import csv

with open('stations.csv', newline='') as infile, open('allstations.csv', newline='', mode='w') as outfile:
    csv_reader = csv.DictReader(infile, delimiter=';')
    csv_writer = csv.writer(outfile, delimiter=';')
    i = 0
    for row in csv_reader:
        csv_writer.writerow([i, float(row['WGS84_Y'].replace(',', '.')),
                             float(row['WGS84_X'].replace(',', '.')), row['Name mit Ort']])
        i += 1
