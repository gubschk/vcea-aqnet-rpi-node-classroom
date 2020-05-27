#!/usr/bin/python2

from Adafruit_BME280 import *
from datetime import datetime
import socket

def main():
    sensor = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
    tstart = time.time()
    while True:
        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()
	date = str(datetime.now())
	 # for Itron Riva
        with open("/run/aqnet/BME280_log2", 'a+') as f:
            f.write(('%s, %s, %s, %.6f, %.6f, %.6f, %.6f')%(date, socket.gethostname(), 'bme280', degrees, pascals, hectopascals, humidity)) 
	    f.write('\n')
	    
	with open("/var/log/wsn/bme280_log", 'a+') as f:
            f.write(('%s, %s, %s, %.6f, %.6f, %.6f, %.6f')%(date, socket.gethostname(), 'bme280', degrees, pascals, hectopascals, humidity)) 
	    f.write('\n')
	    
	time.sleep(29)   
main()
