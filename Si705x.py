#!/usr/bin/python3
from smbus2 import SMBusWrapper, i2c_msg
import time


# I2C Address of the device
SI7050_DEFAULT_ADDRESS			= 0x40

# SI7050 Command Set
SI7050_MEASTEMP_HOLD_CMD		= [0xE3]
SI7050_MEASTEMP_NOHOLD_CMD		= [0xF3]
SI7050_RESET_CMD			= [0xFE]
SI7050_WRITE_USERREG_CMD		= [0xE6]
SI7050_READ_USERREG_CMD			= [0xE7]
SI7050_READ_FW_REV			= [0x84, 0xB8]
SI7050_READ_ID_BYTE1			= [0xFA, 0x0F]
SI7050_READ_ID_BYTE2			= [0xFC, 0xC9]

class Si705x():

	def __init__ (self, bus):
		self.bus = bus

	def _send_cmd (self, cmd, num_bytes = 0):
		w = i2c_msg.write(SI7050_DEFAULT_ADDRESS, cmd)
		if num_bytes:
			r = i2c_msg.read(SI7050_DEFAULT_ADDRESS, num_bytes)
			self.bus.i2c_rdwr(w,r)
			return list(r)
		else:
			self.bus.i2c_rdwr(w)

	def reset(self):
		self._send_cmd(SI7050_RESET_CMD)
		time.sleep(.01)	# the chip needs a little time to come out of reset
	
	def getTemp(self):
		(msb, lsb, crc) = self._send_cmd(SI7050_MEASTEMP_HOLD_CMD, 3)
		crc_init = Si705x.crc8_dallas_maxim(0, msb)
		assert crc == Si705x.crc8_dallas_maxim(crc_init, lsb), "getTemp(): Bad CRC"
		cTemp = ((msb * 256 + lsb) * 175.72 / 65536.0) - 46.85
		fTemp = cTemp * 1.8 + 32
		return cTemp, fTemp
		
	def readUserRegister(self):
		return self._send_cmd(SI7050_READ_USERREG_CMD, 1)[0]

	def writeUserRegister(self, res1, res0):
		# Following read-modify-write approach as per datasheet
		current = self.readUserRegister()
		res1 <<= 7
		if res1:
			current |= res1
		else:
			current &= ~res1	
		if res0:
			current |= res0
		else:
			current &= ~res0	
		setting = SI7050_WRITE_USERREG_CMD
		setting.append(current)
		w = i2c_msg.write(SI7050_DEFAULT_ADDRESS, setting)
		self.bus.i2c_rdwr(w)

	def getSerialNumber(self):
		# Left nibble of SN
		first_access = self._send_cmd(SI7050_READ_ID_BYTE1, 8)
		# Break down the data into (data, crc) tuples
		print(first_access)
		chunks = (first_access[x:x+2] for x in range(0, len(first_access), 2))
		crc_init = 0
		sna = []
		for data, crc in chunks:
			assert crc == Si705x.crc8_dallas_maxim(crc_init, data), "Bad CRC: byte:{}".format(data)
			sna.append(data)
			crc_init = crc

		# Right nibble of SN
		second_access = self._send_cmd(SI7050_READ_ID_BYTE2, 6)
		chunks = (second_access[x:x+3] for x in range(0, len(second_access), 3))
		crc_init = 0
		snb = []
		for data1, data2, crc in chunks:
			crc_init = crc8_dallas_maxim(crc_init, data1)
			assert crc == Si705x.crc8_dallas_maxim(crc_init, data2), "Bad CRC: byte:{}".format(data)
			snb.extend([data1, data2])
			crc_init = crc
			
		return sna + snb

	def getFirmwareRevision(self):
		return self._send_cmd(SI7050_READ_FW_REV, 1)[0]

	@staticmethod
	def crc8_dallas_maxim(crc, a):
		crc ^= a
		for _ in range(8):
			if crc & 0x80:
				crc = ((crc << 1) ^ 0x31) % 256
			else:
				crc = (crc << 1) % 256
		return crc
