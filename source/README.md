# C.H.I.P. GPIO Breakout Python Libraries & Example Program


## Files

<table>
  <tr><th>File</th><th>Description</th></tr>
  <tr><td>spiLib.py</td><td>SPI multiplexer library</td></tr>
  <tr><td>max5702.py</td><td>MAX5702 12 Bit 2 Channel DAC Library</td></tr>
  <tr><td>max11629.py</td><td>MAX11629 12 Bit 8 Channel ADC Library</td></tr>
  <tr><td>io_breakout.py</td><td>A graphical interface for controlling the ADC and DAC</td></tr>
  <tr><td>sine.py</td><td>A script that generates a sine wave on DAC_0 as fast as possible</td></tr>
  <tr><td>interface.glade</td><td>The UI for io_breakout.py</td></tr>
  <tr><td>spi2.dts</td><td>The device tree overlay source for SPI</td></tr>
  <tr><td>spi2.dtbo</td><td>The compiled device tree overlay for SPI</td></tr>
</table>

## The Example Program
The program will read the ADC and display the voltage of all channels 10 times per second when in run mode.<br/>
Clicking the single button will read all channels once.<br/>
The DAC outputs will update immediatly when the values are changed. Enter a value between 0 and 4095 in the input and press enter to apply. Using the up/down arrows will apply it immediatly.<br/>
The voltage reference can be set to 2.048V or 2.5V. This sets the maximum input voltage of the ADC and the maximum output voltage of the DAC.<br/>
If the external reference is selected, you can apply between 1.24V and 3.3V to the Ref In pin. Enter the voltage of the external reference in the numeric input so the ADC and DAC voltages are displayed correctly.
To run this program, you need to install [spidev](https://pypi.python.org/pypi/spidev) and [CHIP_IO](https://github.com/xtacocorex/CHIP_IO).<br/>
The spi2 device tree overlay must be loaded as well as the spidev kernel module. The program must be run as root in order to control the SPI and GPIO.

<img src="https://github.com/cmnybo/chip_io_breakout/raw/master/img/io_interface_screenshot.png" alt="screenshot of the example program"></img>

## Library Usage
The spidev and CHIP_IO python libraries must be installed, the spi device tree overlay and spidev module must be loaded, and python must be run as root for this to work.

Import libraries</br>
`import spiLib, max5702, max11629, time`

Open SPI device</br>
`spi = spiLib.SPI(32766, 0)`</br>
`spi.open()`

Create instance of ADC and DAC</br>
`adc = max11629.MAX11629(spi, 0)`</br>
`dac = max5702.MAX5702(spi, 1)`

Configure voltage references</br>
`adc.vRef(False) # disable internal ADC reference`</br>
`dac.vRef(True, dac.REF_20) # enable internal DAC 2.048V reference`

Write to the DAC. Maximum value is 4095.</br>
`dac.write(dac.DAC_0, 1024) # set channel 0 to 0.512V`</br>
`dac.write(dac.DAC_1, 2048) # set channel 1 to 1.024V`

Perform an ADC conversion</br>
`adc.convert(0) # start conversion on channel 0`</br>
`data = adc.read(1,False) # read one entry from ADC FIFO`</br>
`print (((data[0] << 8) | data[1]) & 0x0FFF) # print the ADC reading`

Perform an ADC scan</br>
`adc.scan() # starts a conversion on channels 0-7. takes about 30µs`</br>
`data = adc.read(8,False) # read 8 entries from ADC FIFO`</br>
`time.sleep(0.0001) # give it some time to finish the conversions`</br>
`# print all 8 channels`</br>
`for i in range(0, 16, 2): print (((data[i] << 8) | data[i+1]) & 0x0FFF)`

Clean up. You must run these before exiting your program to free up the SPI and GPIO pins.</br>
`spi.close()`</br>
`spi.cleanup()`</br>


## License

This program is free software; you can redistribute it and/or modify</br>
it under the terms of the GNU General Public License as published by</br>
the Free Software Foundation; either version 2 of the License, or</br>
(at your option) any later version.</br>

This program is distributed in the hope that it will be useful,</br>
but WITHOUT ANY WARRANTY; without even the implied warranty of</br>
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the</br>
GNU General Public License for more details.</br>

You should have received a copy of the GNU General Public License</br>
along with this program; if not, write to the Free Software</br>
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,</br>
MA 02110-1301, USA.</br>
