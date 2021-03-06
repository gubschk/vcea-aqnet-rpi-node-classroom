#!/usr/bin/python

# Script to access data from WSU Smart Cities sensors.
#
# <https://bitbucket.org/wsular/urbanova-aqnet-proto>


# redirect `print`s to HDMI display
console = open('/dev/tty1', 'w')
import sys
sys.stdout = console
sys.stderr = console
print('\n\nStarting air quality sensors...')

from datetime import datetime
# Create a unique filename
import os
savedir = '/var/log/aqnet/covid_multisensor_data'
try:
    os.makedirs(savedir)
except OSError:
    if not os.path.isdir(savedir):
        raise
localFile  = savedir+'/aq.'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.csv'
# Write header to the local and remote files.
header     = 'Time,CO2, Pressure,Temperature,PM1,PM2_5,PM10\n'
#    ....LOCAL
f          = open(localFile,'w')
f.write('Time, CO2, Pressure, Temperature, PM1, PM2_5, PM10\n')
f.close()

# Initialize the Ultimate GPS Breakout
import gps
ugps = gps.gps("localhost", "2947")
ugps.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
print('    GPS connected!')

# Initialize the BME280 temperature/pressure/humidity sensor.
from Adafruit_BME280 import *
bme280 = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
print('    BME280 connected!')

# RH/T sensor
#sys.path.append('/home/pi/weather-station')
#from HTU21D import HTU21D
#htu21d = HTU21D()
#print('    HTU21D connected!')

# Initialize the K-30 carbon dioxide sensor.
import serial
import time
ser = serial.Serial('/dev/ttyAMA0')
print('    K-30 Serial Connected!')
ser.flushInput()
time.sleep(1)

# Initialize the OPC-N2 particle monitor.
import spidev
import opc
spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 1
spi.max_speed_hz = 500000
alpha = opc.OPCN2(spi)
print('    OPC-N2 connected!')
# Turn sensor on.
time.sleep(1)
alpha.on()


import atexit
@atexit.register
def cleanup():
    alpha.off()


# Read data from both sensors every 1 second.
while True:
    try:
        ser.write('\xFE\x44\x00\x08\x02\x9F\x25')
        time.sleep(.01)
        resp = ser.read(7)
        high = ord(resp[3])
        low  = ord(resp[4])
        co2  = (high*256) + low
        time.sleep(1)
        hist = alpha.histogram()
        print('')
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print('K30     CO2   {:0.1f} ppm'.format(co2))
        print('BME280  tmpr  {:0.2f} degC'.format(bme280.read_temperature()))
        print('        press {:0.1f} kPa'.format(bme280.read_pressure()/1000.))
	print('        RH    {:0.1f} %'.format(bme280.read_humidity()))
#        print('HTU21D  tmpr  {:0.2f} degC'.format(htu21d.read_temperature()))
#        print('        RH    {:0.1f} %'.format(hti21d.read_humidity()))
        print('OPC-N2  PM1   {:0.2f} ug/m^3'.format(hist['PM1']))
        print('        PM2.5 {:0.2f} ug/m^3'.format(hist['PM2.5']))
        print('        PM10  {:0.2f} ug/m^3'.format(hist['PM10']))
        print('    samp freq {:0.2f} sec'.format(hist['Sampling Period']))
        f = open(localFile,'a')
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+','+str(co2)+','+str(bmp280.read_temperature())+','+str(bmp280.read_pressure())+','+str(hist['PM1'])+','+str(hist['PM2.5'])+','+str(hist['PM10'])+'\n')
        f.close()
        time.sleep(29)
    except KeyboardInterrupt, SystemExit:
        raise
    except:
        print('Exception encountered! Ignoring...')


