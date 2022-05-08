#!/usr/bin/env python3

from pymavlink.DFReader import DFReader_binary, DFReader_text
from rdp import rdp
import sys
import csv

def parse_log(log):
    path = []
    while True:
        m = log.recv_match(type='AHR2')
        if m is None:
            break
        m = m.to_dict()
        path.append([m['Lat'], m['Lng'], m['Alt']])
    return path

if __name__ == "__main__":
    filename = sys.argv[1]
    if filename.endswith('.log'):
        log = DFReader_text(filename)
    else:
        log = DFReader_binary(filename)

    path = parse_log(log)

    # Use the first waypoint in the log as the new home
    home = {'Lat': path[0][0], 'Lng': path[0][1], 'Alt': path[0][2]}

    # This method does not work near the north or south poles
    simplified_path = rdp(path, epsilon = 0.0001)

    print(f"Simplified from {len(path)} to {len(simplified_path)} points.")

    with open('mission.txt', 'w') as f:
        f.write("QGC WPL 110\n")

        writer = csv.writer(f, delimiter='\t')
        writer.writerow([0, 1, 0, 16, 0, 0, 0, 0, home['Lat'], home['Lng'], home['Alt'], 1])
        for index, [lat, lon, alt] in enumerate(simplified_path[1:]):
            writer.writerow([index+1, 0, 3, 16, 0, 0, 0, 0, lat, lon, alt, 1])
