# si705x
Python library for communicating with Silicon Labs' Si705x I2C temperature sensors - along with sample apps. Runs on OrangePi (tested) and RaspPi. Uses SMBus2 module.

Simple temperature logger tool is included.

Datasheet: https://www.silabs.com/documents/public/data-sheets/Si7050-1-3-4-5-A20.pdf

## Simple temperature sensing
```python
from smbus2 import SMBusWrapper
from Si705x import Si705x as sensor

with SMBusWrapper(0) as bus:

	c, f = sensir(bus).getTemp()
	print("{:.1f} Celsius, {:.1f} Fahrenheit".format(c, f))
  ```
