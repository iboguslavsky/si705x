#!/usr/bin/python3

from smbus2 import SMBusWrapper
from Si705x import Si705x as sensor

with SMBusWrapper(0) as bus:

	c, f = sensor(bus).getTemp()
	print("{:.1f} Celsius, {:.1f} Fahrenheit".format(c, f))
