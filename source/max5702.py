# -*- coding: utf-8 -*-

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import spiLib

class MAX5702(object):
  DAC_0         = 0x00  # Specify DAC 0
  DAC_1         = 0x01  # Specify DAC 1
  DAC_ALL       = 0x08  # Specify all DACs
  REF_EXT       = 0x00  # Use external reference
  REF_25        = 0x01  # Use internal 2.5V ref
  REF_20        = 0x02  # Use internal 2.048V ref
  REF_41        = 0x03  # Use internal 4.096V ref (Doesn't work with 3.3V supply)
  PWR_ON        = 0x00  # Power on
  PWR_OFF       = 0x03  # Power off Hi-Z output
  PWR_OFF_1K    = 0x01  # Power off 1K Pulldown
  PWR_OFF_100K  = 0x02  # Power off 100K Pulldown
  
  def __init__(self, spi, ch):
    self.spi = spi
    self.channel = ch
    self.configSPI()
    self.spi.write([0x51, 0x00, 0x00])   # Reset DAC
    self.spi.write([0x76, 0x00, 0x00])   # Set reference to 2.048V
    self.spi.write([0x40, 0x03, 0x00])   # Power up both DACs

  def configSPI(self):
    # configure spi settings
    # Supports SPI mode 1, MSB first, 33MHz Max
    self.spi.setChannel(self.channel)
    self.spi.config(5000, 0x1, False)
  
  def code(self, dac, value):
    # Writes to code register on selected dac
    if (int(value) > 4095): value = 4095
    if (int(value) < 0):    value = 0
    
    cmd  = 0x00 | (int(dac) & 0x0F)
    lVal = (int(val) << 4) & 0xFF
    hVal = (int(val) >> 4) & 0xFF
    
    self.configSPI()
    self.spi.write([cmd, hVal, lVal])
  
  def load(self, dac):
    # Loads code register on selected dac
    cmd  = 0x10 | (int(dac) & 0x0F)
    
    self.configSPI()
    self.spi.write([cmd, 0x00, 0x00])
  
  def write(self, dac, val):
    # Writes code register and loads on selected dac
    if (int(val) > 4095): val = 4095
    if (int(val) < 0):    val = 0
    
    cmd  = 0x30 | (int(dac) & 0x0F)
    lVal = (int(val) << 4) & 0xFF
    hVal = (int(val) >> 4) & 0xFF
    
    self.configSPI()
    self.spi.write([cmd, hVal, lVal])
    
  def clear(self):
    # Clears all code & dac registers
    self.configSPI()
    self.spi.write([0x50, 0x00, 0x00])
    
  def reset(self):
    # Resets all registers
    self.configSPI()
    self.spi.write([0x51, 0x00, 0x00])
    
  def vRef(self, enable, level):
    # enables reference and sets level
    en = 0x04 if (bool(enable)) else 0x00
    cmd  = 0x70 | en | (int(level) & 0x03)
    
    self.configSPI()
    self.spi.write([cmd, 0x00, 0x00])
  
  def power(self, dac, pwr):
    # Sets power mode for the dacs
    cmd = 0x40 | (int(dac) & 0x03)
    dacs = {0x0:0x1, 0x1:0x2, 0x8:0x3}.get(int(pwr), 0x3)
    
    self.configSPI()
    self.spi.write([cmd, dacs, 0x00])
