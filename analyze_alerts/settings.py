""" Configure file path """
import os

def init(year, timezone_offset):
	global traffic_year, tz_offset
	
	traffic_year = year
	tz_offset = timezone_offset

