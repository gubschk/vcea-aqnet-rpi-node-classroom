#!/usr/bin/python2
#
# Acquire data from OPC-N2
#
# Patrick O'Keeffe <pokeeffe@wsu.edu>
# Laboratory for Atmospheric Research at Washington State University

from __future__ import print_function
from Adafruit_BME280 import *
from datetime import datetime


import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

import serial

import os, os.path as osp
import time
import socket
import json

import spidev
import opc

#### read config file
import ConfigParser as configparser
c = configparser.ConfigParser()
c.read('../etc/wsn/opcn2-logger.conf')

interval = c.getint('main', 'interval')
log_dir = c.get('logging', 'log_dir')
log_file = c.get('logging', 'log_file')
#######################################

#### logging setup
try:
    os.makedirs(log_dir)
except OSError:
    if not osp.isdir(log_dir):
        raise

tsfmt = '%Y-%m-%d %H:%M:%S'
jsonfmt = '{"%(asctime)s": %(message)s}'
log_fmt = logging.Formatter(jsonfmt,
                            datefmt=tsfmt)
log_file = TimedRotatingFileHandler(osp.join(log_dir, log_file),
                                    when='D', interval=30)
log_file.setFormatter(log_fmt)
log_file.suffix = '%Y-%m-%d.jsonl'
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(log_file)

# for debugging
#log.addHandler(logging.StreamHandler())

# for urbanova
rundir = '/run/aqnet/opcn2/'
try:
    os.makedirs(rundir)
except OSError:
    if not osp.isdir(rundir):
        raise

spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 1
spi.max_speed_hz = 500000
alphasense = opc.OPCN2(spi)

alphasense.on()

#import atexit
#@atexit.register
#def cleanup():
#    opc.off()


#while True:
#    try:
#        data = opc.histogram()
#        now = time.time()

#        jsondata = {}
#        for k,v in data.items():
#            clean_name = k.replace(' ','_')
#	    date = str(datetime.now())
#            string_val = 'NAN' if v is None else str(v)
#            jsondata[clean_name] = string_val

 #           with open(rundir+clean_name, 'a+') as f:
#                f.write(date + ', ' + socket.gethostname() + ', ' + string_val + '\n')

        # monthly-rotated flat json files
 #       log.info(json.dumps(data))

#        time.sleep(interval)
#    except (KeyboardInterrupt, SystemExit):
#        opc.off()
#        raise
#    except:
#        time.sleep(15)
#        pass

#!/usr/bin/python2
#
# Acquire data from K30 CO2 sensor and do stuff
#
# Laboratory for Atmospheric Research at Washington State University
#!/usr/bin/python2


#### read config file
import ConfigParser as configparser
c = configparser.ConfigParser()
c.read('../etc/wsn/k30-logger.conf')

serial_port = c.get('main', 'serial_port')
serial_baud = c.getint('main', 'serial_baud')
interval = c.getint('main', 'interval')
log_dir = c.get('logging', 'log_dir')
log_file = c.get('logging', 'log_file')
#broker_addr = c.get('mqtt', 'broker_addr')
#broker_port = c.get('mqtt', 'broker_port')
#_template = c.get('mqtt', 'report_topic')
#report_topic = _template.format(hostname=socket.gethostname())

#### logging setup
try:
    os.makedirs(log_dir)
except OSError:
    if not osp.isdir(log_dir):
        raise

# HINT alt. solution to http://stackoverflow.com/a/27858760
# XXXX does not handle partial-hour UTC offsets
#tzstr = '{:+03d}00'.format(-time.timezone/3600)
tsfmt = '%Y-%m-%dT%H:%M:%S'#+tzstr

log_fmt = logging.Formatter('%(asctime)s\t%(message)s',
                            datefmt=tsfmt)
tsv_file = TimedRotatingFileHandler(osp.join(log_dir, log_file),
                                    when='D', interval=30)
tsv_file.setFormatter(log_fmt)
tsv_file.suffix = '%Y-%m-%d.tsv'
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(tsv_file)

#log.addHandler(logging.StreamHandler()) # for debugging

##### MQTT integration
#client = paho.Client()
#client.connect(broker_addr, broker_port)
#client.loop_start()
#report = '{{"tstamp": {ts:0.2f}, "CO2": {co2:0.0f}}}'

# for urbanova
rundir = '/run/aqnet'
runfile = os.path.join(rundir, 'CO2')
#try:
#    os.makedirs(rundir)
#except OSError:
#    if not osp.isdir(rundir):
#        raise
    
#For COVID research
savedir = '/var/log/wsn/covid_OPC_and_CO2_data'
savefile = savedir + '/aq.'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.csv'


try:
    os.makedirs(savedir)
except OSError:
    if not osp.isdir(rundir):
        raise
    
BME_dir = '/var/log/wsn/covid_BME_data'
BME_file = BME_dir + '/aq.'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.csv'

try:
    os.makedirs(BME_dir)
except OSError:
    if not osp.isdir(rundir):
        raise

k30 = serial.Serial(serial_port, serial_baud, timeout=1)

def get_co2(device):
    device.write('\xFE\x44\x00\x08\x02\x9F\x25')
    time.sleep(0.010)
    response = device.read(7)
    high, low = ord(response[3]), ord(response[4])
    return ((high << 8) | low)

sensor = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
tstart = time.time()

while True:
    try:
        
        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()
	date = str(datetime.now())
	
	 # for Itron Riva
        with open("/run/aqnet/BME280_log2", 'a+') as f:
            f.write(('%s, %s, %s, %.6f, %.6f, %.6f, %.6f')%(date, socket.gethostname(), 'bme280', degrees, pascals, hectopascals, humidity)) 
	    f.write('\n')
	    
	with open(BME_file, 'a+') as f:
            f.write(('%s, %s, %s, %.6f, %.6f, %.6f, %.6f')%(date, socket.gethostname(), 'bme280', degrees, pascals, hectopascals, humidity)) 
	    f.write('\n')

	date = str(datetime.now())
        co2 = get_co2(k30)
        date = str(datetime.now())
        now = time.time()
#        data = opc.histogram()
#        now = time.time()
        hist = alphasense.histogram()

        # for journlctl logs
        print('{{"co2": {:0.0f}}}'.format(co2))
#        print('BME280  tmpr  {:0.2f} degC'.format(bme280.read_temperature()))
#        print('        press {:0.1f} kPa'.format(bme280.read_pressure()/1000.))
        print('OPC-N2  PM1   {:0.2f} ug/m^3'.format(hist['PM1']))
        print('        PM2.5 {:0.2f} ug/m^3'.format(hist['PM2.5']))
        print('        PM10  {:0.2f} ug/m^3'.format(hist['PM10']))
#        print('    samp freq {:0.2f} sec'.format(hist['Sampling Period']))

        
        # for Itron Riva
        with open(runfile, 'a+') as f:
            f.write(date + ',' + socket.gethostname() + ',' + str(co2))
            f.write('\n')
	#client.publish(report_topic,
        #               report.format(ts=now, co2=co2),
        #               qos=1, retain=True)
#        degrees = sensor.read_temperature()
#        pascals = sensor.read_pressure()
#        hectopascals = pascals / 100
#        humidity = sensor.read_humidity()
#        with open(savefile, 'a+') as f:
#            header = 'Date/Time,CO2, Pressure (pascals),Temperature,PM1,PM2_5,PM10\n'
#            f.write(header)
#            f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+','+str(co2)+','+str(degrees)+','+str(pascals)+','+ str(humidity) +str(hist['PM1'])+','+str(hist['PM2.5'])+','+str(hist['PM10'])+'\n')
#           f.write(str(datetime.now()) + ', ' + str(co2))
#            f.write('\n')
        with open(savefile, 'a+') as f:
            f.write(str(datetime.now()) + ', ' + str(co2) + ', ' + str(hist['PM1'])+ ', ' +str(hist['PM2.5'])+ ', '  +str(hist['PM10']))
#            f.write(str(datetime.now()) + ', ' + str(co2) + ', ' + str(pressure) + ', ' + str(temperature) + ', ' + str(hist['PM1'])+', '+str(hist['PM2.5'])+',' +str(hist['PM10']))
	    f.write('\n')
#	with open("/var/log/wsn/COVID-bme280-log", 'a+') as f:
#            f.write(('%s, %s, %s, %.6f, %.6f, %.6f, %.6f')%(date, socket.gethostname(), 'bme280', degrees, pascals, humidity)) 
#	    f.write('\n')

        time.sleep(interval)
    except (KeyboardInterrupt, SystemExit):
        k30.close()
        client.loop_stop()
        raise
    except:
        time.sleep(5)
        pass
    
#!/usr/bin/python2

#from Adafruit_BME280 import *
#from datetime import datetime
#import socket

#def main():
#    sensor = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
#    tstart = time.time()
#    while True:
#        degrees = sensor.read_temperature()
#        pascals = sensor.read_pressure()
#        hectopascals = pascals / 100
#        humidity = sensor.read_humidity()
#        date = str(datetime.now())
	 # for Itron Riva
#        with open("/run/aqnet/BME280_log2", 'a+') as f:
#            f.write(('%s, %s, %s, %.6f, %.6f, %.6f, %.6f')%(date, socket.gethostname(), 'bme280', degrees, pascals, hectopascals, humidity)) 
#            f.write('\n')
	    
#        with open("/var/log/wsn/bme280_log", 'a+') as f:
#            f.write(('%s, %s, %s, %.6f, %.6f, %.6f, %.6f')%(date, socket.gethostname(), 'bme280', degrees, pascals, hectopascals, humidity))
#            f.write('\n')
	    
#        time.sleep(29)   
#main()
