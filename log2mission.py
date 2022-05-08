#!/usr/bin/env python3

from pymavlink.DFReader import DFReader_binary, DFReader_text
from rdp import rdp
import sys
import csv

def parse_path(log):
    path = []
    while True:
        m = log.recv_match(type='AHR2')
        if m is None:
            break
        m = m.to_dict()
        path.append([m['Lat'], m['Lng'], m['Alt']])

    return path

def parse_home(log):
    return {"Lat": 123, "Lng": 456, "Alt": 789} # todo

if __name__ == "__main__":
    filename = sys.argv[1]
    if filename.endswith('.log'):
        log = DFReader_text(filename)
    else:
        log = DFReader_binary(filename)

    path = parse_path(log)
    home = parse_home(log)

    # This method does not work near the north or south poles
    simplified_path = rdp(path, epsilon = 0.0001)

    print(f"Simplified from {len(path)} to {len(simplified_path)} points.")

    with open('mission.txt', 'w') as f:
        f.write("QGC WPL 110\n")

        writer = csv.writer(f, delimiter='\t')
        writer.writerow([0, 1, 0, 16, 0, 0, 0, 0, home['Lat'], home['Lng'], home['Alt'], 1])
        for index, [lat, lon, alt] in enumerate(simplified_path[1:]):
            writer.writerow([index+1, 0, 3, 16, 0, 0, 0, 0, lat, lon, alt, 1])
