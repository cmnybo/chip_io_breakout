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

import time
import CHIP_IO.GPIO as GPIO
import spiLib

class MAX11629(object):
  AVG_1   = 0x20  # Averaging disabled
  AVG_4   = 0x30  # 4 Averages
  AVG_8   = 0x34  # 8 Averages
  AVG_16  = 0x38  # 16 Averages
  AVG_32  = 0x3C  # 32 Averages
  
  def __init__(self, spi, ch):
    self.spi = spi
    self.channel = ch
    self.avg = 1
    self.adc = 0
    
    # configure conversion complete pin
    GPIO.setup("AP-EINT1", GPIO.IN)
    
    # configure ADC
    self.configSPI()
    self.spi.write([0x18]) # reset
    self.spi.write([0x68]) # internal vref, self timed conversions
    self.spi.write([0x40]) # no averaging
  
  def read(self, numRdg, force):
    # read from ADC FIFO. Waits for conversion complete unless force is true
    if (int(numRdg) > 16): numRdg = 16
    if (int(numRdg) < 1):  numRdg = 1
    
    if (not GPIO.input("AP-EINT1") or bool(force)):
      # conversion complete or forced read
      pass
    else:
      # waiting for conversion complete
      for i in range(0,10):
        if (not GPIO.input("AP-EINT1")):
          break
        else:
          time.sleep(0.0001)
      # Interrupts are not working reliably.
      # I think the interrupt is being fired before the code to wait for it runs.
      # The ADC runs at 300K samples per second.
      #GPIO.wait_for_edge("AP-EINT1", GPIO.FALLING)
    
    return self.spi.read(int(numRdg)*2)
  
  def configSPI(self):
    # configure spi settings
    # Supports modes 0 & 3, MSB first, 10MHz Max
    self.spi.setChannel(self.channel)
    self.spi.config(5000, 0x0, False)
    
  def convert(self, channel):
    # starts conversion on adc channel (0-7)
    # the last 16 conversions are stored in the FIFO
    if (channel > 7): channel = 7
    if (channel < 0): channel = 0
    
    ch  = ((int(channel) & 0x07) << 3)
    self.configSPI()
    self.spi.write([0x86 | ch])
  
  def scan(self):
    # starts conversion on all channels
    self.configSPI()
    self.spi.write([0xC0])
    
  def averaging(self, avg):
    # sets the number of averages (1,4,8,16,32)
    self.configSPI()
    self.spi.write([int(avg)])
  
  def vRef(self, en):
    # enable internal voltage reference (2.5V)
    self.configSPI()
    if (bool(en)):
      self.spi.write([0x68])
    else:
      self.spi.write([0x64])
