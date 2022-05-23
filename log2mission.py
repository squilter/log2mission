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

    # Put all points at alt = 0, so the algorithm only simplifies the path as seen from above
    # Note that this introduces a risk of a straight-line path that actually changes altitude where this altitude change is lost.
    path_ecef = navpy.lla2ecef(lat, lon, [0] * len(lat), latlon_unit='deg', alt_unit='m', model='wgs84')
    simplified_path_ecef = rdp(path_ecef, epsilon = 1.3)
    lat_simplified, lon_simplified, _ = navpy.ecef2lla(simplified_path_ecef, latlon_unit='deg')

    alt_simplified = []
    latlons = list(zip(lat, lon))
    # Figure out what altitude was associated with the points that were kept
    for latlon_simplified in zip(lat_simplified, lon_simplified):
        idx = None
        for i, latlon in enumerate(latlons):
            if abs(latlon[0] - latlon_simplified[0]) + abs(latlon[1] - latlon_simplified[1]) < 0.0000000001:
                idx = i
                break
        alt_simplified.append(alt[idx])

    assert len(alt_simplified) == len(lat_simplified), "Something went horribly wrong with altitude reconstruction..."

    print(f"Simplified from {len(lat)} to {len(lat_simplified)} points.")

    write_mission(lat_simplified, lon_simplified, alt_simplified)
