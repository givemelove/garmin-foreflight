import os
import argparse
import xml.etree.ElementTree as ET
import math
from datetime import datetime

# Calculates the groundspeed given two lat/long coordinates and associated start/end datetimes.
def calcSpeed(fm, to, start, end):
    dx = math.hypot(*[b - a for a, b in zip(fm, to)]) * 60.0 # nautical miles
    dt = (end - start).total_seconds() / 3600.0 # hours
    return round(dx / dt) if dt else 0

def convertFile(input):
	hdr = '  Lcl Date, Lcl Time, UTCOfst, AtvWpt,     Latitude,    Longitude,    AltB, BaroA,  AltMSL,   OAT,    IAS, GndSpd,    VSpd,  Pitch,   Roll,  LatAc, NormAc,   HDG,   TRK, volt1,  FQtyL,  FQtyR, E1 FFlow, E1 FPres, E1 OilT, E1 OilP, E1 MAP, E1 RPM, E1 CHT1, E1 CHT2, E1 CHT3, E1 CHT4, E1 EGT1, E1 EGT2, E1 EGT3, E1 EGT4,  AltGPS, TAS, HSIS,    CRS,   NAV1,   NAV2,    COM1,    COM2,   HCDI,   VCDI, WndSpd, WndDr, WptDst, WptBrg, MagVar, AfcsOn, RollM, PitchM, RollC, PichC, VSpdG, GPSfix,  HAL,   VAL, HPLwas, HPLfd, VPLwas'
	fmt = '{date}, {time},   00:00,       , {lat: >12}, {lng: >12},        ,      , {alt: >7},      ,       , {gspd: >6}'
	tail = ',        ,       ,       ,       ,       ,      ,      ,      ,       ,       ,         ,         ,        ,        ,       ,       ,        ,        ,        ,        ,        ,        ,        ,        ,        ,    ,     ,       ,       ,       ,        ,        ,       ,       ,       ,      ,       ,       ,       ,       ,      ,       ,      ,      ,      ,       ,     ,      ,       ,      ,       '

	# Retrieve the Track Segments from the GPX
	ns = {'': 'http://www.topografix.com/GPX/1/1'}
	try:
		tree = ET.parse(input)
	except IOError as e:
		print(f"{e}")
		return False
	root = tree.getroot()
	segments = root.findall("./trk/trkseg/*", ns)

	# Export the csv header.
	csv = [hdr]


	# Export the csv data.
	fm = None
	start = None
	for segment in segments:
		# Altitude converted in feet
		alt = round(3.280839895 * float(segment.find("./ele", ns).text), 1)

		# Date Modeling
		dt = segment.find("./time", ns).text
		date, time = dt.split('T')
		time = time[:-1].split(".")[0]
		end = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S')

		lat = float(segment.attrib["lat"])
		lng = float(segment.attrib["lon"])
		to = (float(lat), float(lng))

		gspd = calcSpeed(fm, to, start, end) if fm and start else 0

		# Place the current values (to) as the start value for the next calculation
		fm = to
		start = end
		
		# Append data with trailing commas for unset values.
		csv.append(fmt.format(date=date, time=time, lat=lat, lng=lng, alt=alt, gspd=gspd) + tail)

	# Write file to disk.
	with open(input.split(".gpx")[0] + '.csv', 'w') as f:
		f.writelines('\n'.join(csv))
	return True

def main():
	parser = argparse.ArgumentParser(description='Convert your Garmin GPX Activity file to a Foreflight compatible G1000 file.')
	parser.add_argument('input_file')

	args = parser.parse_args()
	input = args.input_file

	return convertFile(input)


if __name__ == '__main__':
	main()
