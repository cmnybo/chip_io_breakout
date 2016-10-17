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

import CHIP_IO.GPIO as GPIO
import spidev

class SPI(object):
  def __init__(self, device, bus):
    GPIO.setup("XIO-P0", GPIO.OUT)
    GPIO.setup("XIO-P1", GPIO.OUT)
    GPIO.setup("XIO-P2", GPIO.OUT)
    
    GPIO.output("XIO-P0", GPIO.LOW)
    GPIO.output("XIO-P1", GPIO.LOW)
    GPIO.output("XIO-P2", GPIO.LOW)
    
    self.spi = spidev.SpiDev();
    self.device = device
    self.bus = bus
    self.isOpen = False
    self.channel = 0
    
  def open(self):
    # Opens SPI bus
    if (not self.isOpen):
      self.spi.open(self.device, self.bus)
      self.isOpen = True
  
  def close(self):
    # Closes SPI bus
    if (self.isOpen):
      self.spi.close()
      self.isOpen = False
  
  def cleanup(self):
    # Unexports GPIO pins
    GPIO.cleanup()

  def config(self, freq, mode, lsbFirst):
    # Sets frequency, mode, and bit order
    if (not self.isOpen):
      print "SPI Bus Not Open"
      return
      
    if (freq > 100000): freq = 100000
    if (freq < 1): freq = 1
    if (mode > 3): mode = 3
    if (mode < 0): mode = 0
    
    self.spi.max_speed_hz = int(freq*1000)   # Sets SPI max speed in KHz
    self.spi.mode = int(mode)                # Sets SPI mode
    self.spi.lsbfirst = bool(lsbFirst)       # Sets SPI bit order
    self.spi.cshigh = False

  def setChannel(self, ch):
    # Sets SPI mux channel
    if (not self.isOpen):
      print "SPI Bus Not Open"
      return
      
    # if the channel is the same, just return
    if (self.channel == ch):
      return
    
    # make sure input is valid
    if (ch < 0): ch = 0
    if (ch > 7): ch = 7
    
    # Sets SPI channel
    GPIO.output("XIO-P0", GPIO.HIGH if (ch & 1) else GPIO.LOW)
    GPIO.output("XIO-P1", GPIO.HIGH if (ch & 2) else GPIO.LOW)
    GPIO.output("XIO-P2", GPIO.HIGH if (ch & 4) else GPIO.LOW)

    print "Channel: " + str(ch)
    self.channel = ch
  
  def write(self, data):
    # Writes data
    if (not self.isOpen):
      print "SPI Bus Not Open"
      return
      
    # Write data to SPI
    if (self.isOpen):
      self.spi.writebytes(data)
    
  def read(self, numBytes):
    # Reads data
    if (not self.isOpen):
      print "SPI Bus Not Open"
      return
      
    # Read numBytes from SPI
    if (self.isOpen):
      return self.spi.readbytes(numBytes)
    else:
      return None
    
  def transfer(self, data):
    # Transfers data bidirectionally
    if (not self.isOpen):
      print "SPI Bus Not Open"
      return
      
    # Bidirectional transfer
    if (self.isOpen):
      return self.spi.xfer(data)
    else:
      return None
