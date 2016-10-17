#!/usr/bin/python

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.


# This script attempts to play a sine wave on DAC_0 as fast as possible

# This script requires spiLib.py & max5702.py
# This script requires spidev and CHIP_IO to be installed
# https://pypi.python.org/pypi/spidev
# https://github.com/xtacocorex/CHIP_IO

import spiLib, max5702
spi = spiLib.SPI(32766, 0)
spi.open()
dac = max5702.MAX5702(spi, 1)
dac.vRef(True, dac.REF_20)

sine = [
256, 278, 300, 322, 343, 364, 384, 402, 420, 437, 452, 465, 477, 488, 
496, 503, 508, 511, 512, 511, 508, 503, 496, 488, 477, 465, 452, 437, 420, 
402, 384, 364, 343, 322, 300, 278, 256, 233, 211, 189, 168, 147, 127, 109, 91, 
74, 59, 46, 34, 23, 15, 8, 3, 0, 0, 0, 3, 8, 15, 23, 34, 46, 59, 74, 91, 109, 
127, 147, 168, 189, 211, 233]

for c in range(0,2000):
	for i in range(0,72):
		dac.write(dac.DAC_0, sine[i])


dac.write(dac.DAC_0, 0)
spi.close()
spi.cleanup()

