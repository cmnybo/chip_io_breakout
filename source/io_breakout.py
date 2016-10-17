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

# This program requires spiLib.py, max5702.py, max11629.py, & interface.glade
# This program requires spidev and CHIP_IO to be installed
# https://pypi.python.org/pypi/spidev
# https://github.com/xtacocorex/CHIP_IO

import gtk, gobject, threading, os, sys, time
import spiLib, max5702, max11629
import CHIP_IO.GPIO as GPIO

class GPIO_Breakout(object):
  def __init__(self):
    gobject.threads_init()
    
    # setup gui
    builder = gtk.Builder()
    builder.add_from_file("interface.glade")
    builder.connect_signals(self)
    # Windows
    self.mainWindow = builder.get_object("mainWindow")
    self.mainWindow.connect("destroy", gtk.main_quit)
    # Buttons
    self.btnRun = builder.get_object("btnRun")
    self.btnSingle = builder.get_object("btnSingle")
    # Radio buttons
    self.radRef = [
      builder.get_object("radRef0"),
      builder.get_object("radRef1"),
      builder.get_object("radRef2")     
    ]    
    # Text boxes
    self.txtADC = [
      builder.get_object("txtADC0"),
      builder.get_object("txtADC1"),
      builder.get_object("txtADC2"),
      builder.get_object("txtADC3"),
      builder.get_object("txtADC4"),
      builder.get_object("txtADC5"),
      builder.get_object("txtADC6"),
      builder.get_object("txtADC7")
    ]
    
    self.txtDAC = [
      builder.get_object("txtDAC0"),
      builder.get_object("txtDAC1")  
    ]
    # Number inputs
    self.numDAC0    = builder.get_object("numDAC0") 
    self.numDAC1    = builder.get_object("numDAC1") 
    self.numExtRef  = builder.get_object("numExtRef") 
    # Adjustments
    self.adjDAC0    = builder.get_object("adjDAC0") 
    self.adjDAC1    = builder.get_object("adjDAC1") 
    self.adjExtRef  = builder.get_object("adjExtRef") 
    
    self.ref = 2.048
    self.extRef = False
    self.run = False
    self.adcVals = [0,0,0,0,0,0,0,0]
    self.dacVals = [0,0]
    
    # ADC read interval: 100ms
    self.adcInt  = 0.1
    
    self.initHardware()
  
  # starts / stops adc updating
  def on_btnRun_toggled(self, button):
    self.run = button.get_active()
    
    if (self.run):
      button.set_label("Stop")
      self.adcTimer = threading.Timer(self.adcInt, self.readADC)
      self.adcTimer.start()
    else:
      button.set_label("Run")
      self.adcTimer.cancel()
  
  # Perform ADC Scan  
  def on_btnSingle_clicked(self, button):
    print "Scanning ADC"
    
    adc.read(16, True) # Empty FIFO first
    adc.scan()
    time.sleep(0.01)    
    # Read data from ADC
    adcData = adc.read(8, False)
    
    # Proccess data and store
    data = []
    for i in range(0,16,2):
      data.append(((adcData[i] << 8) | adcData[i+1]) & 0x0FFF)
    
    self.adcVals = data
    
    self.updateVoltages()
    print "Done Scanning ADC"
  
  # voltage reference changed
  def on_radRef0_toggled(self, button):
    if (button == self.radRef[0]):
      self.ref = 2.048
      self.extRef = False
      dac.vRef(True, dac.REF_20)
    
    elif (button == self.radRef[1]):
      self.ref = 2.5
      self.extRef = False
      dac.vRef(True, dac.REF_25)
      
    elif (button == self.radRef[2]):
      self.ref = self.adjExtRef.get_value()
      self.extRef = True
      dac.vRef(True, dac.REF_EXT)
    
    self.updateVoltages()
  
  # dac0 changed
  def on_numDAC0_value_changed(self, num):
    self.dacVals[0] = self.adjDAC0.get_value()
    self.updateVoltages()
    
    dac.write(dac.DAC_0, self.dacVals[0])
  
  # dac1 changed
  def on_numDAC1_value_changed(self, num):
    self.dacVals[1] = self.adjDAC1.get_value()
    self.updateVoltages()
    
    dac.write(dac.DAC_1, self.dacVals[1])
  
  # external reference voltage changed
  def on_numExtRef_value_changed(self, num):
    if (self.extRef):
      self.ref = self.adjExtRef.get_value()
      self.updateVoltages()
  
  # calculates voltage from adc / dac value
  def calcVoltage(self, value, maxVal,  ref):
    return (ref / maxVal) * value
  
  # updates voltage textboxes
  def updateVoltages(self):
    # ADC voltages
    for i in range(0,8):
      voltage = self.calcVoltage(self.adcVals[i], 4096, self.ref)
      self.txtADC[i].set_text('{:5.3f}V'.format(voltage))
    
    # DAC voltages
    for i in range(0,2):
      voltage = self.calcVoltage(self.dacVals[i], 4096, self.ref)
      self.txtDAC[i].set_text('{:5.3f}V'.format(voltage))

  # reads adc and starts display update
  def readADC(self):
    def update():
      gtk.threads_enter()
      try:
        self.updateVoltages()
        
      finally:
        gtk.threads_leave()
    
    # Perform ADC Scan
    adc.read(16, True) # Empty FIFO first
    adc.scan()
    time.sleep(0.001) 
    # Read data from ADC
    adcData = adc.read(8, False)
    
    # Proccess data and store
    data = []
    for i in range(0,16,2):
      data.append(((adcData[i] << 8) | adcData[i+1]) & 0x0FFF)
    self.adcVals = data
    
    # Update text boxes
    gobject.idle_add(update)
    
    # Restart timer
    self.adcTimer = threading.Timer(self.adcInt, self.readADC)
    self.adcTimer.start()
  
  # configures voltage references
  def initHardware(self):
    dac.vRef(True, dac.REF_20)
    adc.vRef(False)
  
if __name__ == "__main__":
  os.chdir(sys.path[0])
  
  # open spi
  spi = spiLib.SPI(32766, 0)
  spi.open()
  
  # initilize DAC and ADC
  dac = max5702.MAX5702(spi, 1)
  adc = max11629.MAX11629(spi, 0)
  adc.read(16, True)    # clear ADC FIFO
  
  # show main window and start main thread
  io = GPIO_Breakout()
  io.mainWindow.show()
  gtk.main()
  
  # close spi on exit
  spi.close()
  spi.cleanup()


