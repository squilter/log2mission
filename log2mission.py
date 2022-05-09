#!/usr/bin/env python3

from pymavlink.DFReader import DFReader_binary, DFReader_text
from rdp import rdp
import navpy
import sys
import csv

def parse_log(log):
    lat = []
    lon = []
    alt = []
    while True:
        m = log.recv_match(type='AHR2')
        if m is None:
            break
        m = m.to_dict()
        lat.append(m['Lat'])
        lon.append(m['Lng'])
        alt.append(m['Alt'])
    return lat, lon, alt

if __name__ == "__main__":
    filename = sys.argv[1]
    if filename.endswith('.log'):
        log = DFReader_text(filename)
    else:
        log = DFReader_binary(filename)

    lat, lon, alt = parse_log(log)

    # Use the first waypoint in the log as the new home
    home = {'Lat': lat[0], 'Lng': lon[1], 'Alt': alt[2]}

    path_ecef = navpy.lla2ecef(lat, lon, alt, latlon_unit='deg', alt_unit='m', model='wgs84')

    simplified_path_ecef = rdp(path_ecef, epsilon = 0.5)

    lat_simplified, lon_simplified, alt_simplified = navpy.ecef2lla(simplified_path_ecef, latlon_unit='deg')
    
    print(f"Simplified from {len(lat)} to {len(lat_simplified)} points.")

    with open('mission.txt', 'w') as f:
        f.write("QGC WPL 110\n")
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([0, 1, 0, 16, 0, 0, 0, 0, home['Lat'], home['Lng'], home['Alt'], 1])
        for index, [lat, lon, alt] in enumerate(zip(lat_simplified, lon_simplified, alt_simplified)):
            writer.writerow([index+1, 0, 3, 16, 0, 0, 0, 0, lat, lon, alt, 1])
