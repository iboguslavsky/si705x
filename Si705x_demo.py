#!/usr/bin/python3
from smbus2 import SMBusWrapper, i2c_msg
from Si705x import Si705x as Si705x


with SMBusWrapper(0) as bus:

	sensor = Si705x(bus)
	print("Resetting...")
	sensor.reset()

	tempC, tempF = sensor.getTemp()
	print("Temperature: {0:.1f}C, {1:.1f}F".format(tempC, tempF))

	user_register = sensor.readUserRegister()
	res0 = user_register & 0x01
	res1 = user_register & 0x80
	adc_resolution = res1 << 1 + res0
	vdds = user_register & 0b01000000
	print("ADC Resolution: {} bits".format(14 - adc_resolution))
	print("Voltage status: {}".format("ok" if not vdds else "Low"))
	print("User register: 0x{0:x}".format(user_register))
	print("Firware version: 0x{0:x}".format(sensor.getFirmwareRevision()))

	serial = sensor.getSerialNumber()
	serial_hex = ":".join("{:02x}".format(byte) for byte in serial)
	print("Serial number (CRC OK): {}".format(serial_hex))
	# SNB3 contains part number info
	print("Part Number: Si70{}".format(serial[4]))

	print("Set ADC resolution to 11 bit")
	sensor.writeUserRegister(res1 = 1, res0 = 1)
	user_register = sensor.readUserRegister()
	print("User register: 0x{0:x}".format(user_register))
	tempC, tempF = sensor.getTemp()
	print("Temperature: {0:.1f}C, {1:.1f}F".format(tempC, tempF))
