#!/usr/bin/python3 -u
from datetime import datetime
from smbus2 import SMBusWrapper
from Si705x import Si705x as temp_sensor
import time


with SMBusWrapper(0) as bus:

	sensor = temp_sensor(bus)
	while True:
		(c, f) = sensor.getTemp()
		print("{0:}, {1:.1f}C, {2:.1f}F".format(datetime.now(), c, f))
		time.sleep(10)
