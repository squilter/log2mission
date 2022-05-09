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

def write_mission(lat, lon, alt):
    with open('mission.txt', 'w') as f:
        f.write("QGC WPL 110\n")
        writer = csv.writer(f, delimiter='\t')
        # Use the first waypoint in the log as the new home
        writer.writerow([0, 1, 0, 16, 0, 0, 0, 0, lat[0], lon[0], alt[0], 1])
        for index, [lat, lon, alt] in enumerate(zip(lat, lon, alt)):
            writer.writerow([index+1, 0, 0, 16, 0, 0, 0, 0, lat, lon, alt, 1])

if __name__ == "__main__":
    filename = sys.argv[1]
    if filename.endswith('.log'):
        log = DFReader_text(filename)
    else:
        log = DFReader_binary(filename)

    lat, lon, alt = parse_log(log)

    path_ecef = navpy.lla2ecef(lat, lon, alt, latlon_unit='deg', alt_unit='m', model='wgs84')
    simplified_path_ecef = rdp(path_ecef, epsilon = 1.3)
    lat_simplified, lon_simplified, alt_simplified = navpy.ecef2lla(simplified_path_ecef, latlon_unit='deg')

    print(f"Simplified from {len(lat)} to {len(lat_simplified)} points.")

    write_mission(lat_simplified, lon_simplified, alt_simplified)
