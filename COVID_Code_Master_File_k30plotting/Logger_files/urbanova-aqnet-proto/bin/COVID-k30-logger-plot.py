#!/usr/bin/python2
#
# Acquire data from K30 CO2 sensor and do stuff
#
# Laboratory for Atmospheric Research at Washington State University

from __future__ import print_function

import os, os.path as osp
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import csv
import random
import time

import serial
import socket
#import paho.mqtt.client as paho

#### read config file
import ConfigParser as configparser
c = configparser.ConfigParser()
c.read('../etc/wsn/COVID-k30-logger.conf')

serial_port = c.get('main', 'serial_port')
serial_baud = c.getint('main', 'serial_baud')
interval = c.getint('main', 'interval')
log_dir = c.get('logging', 'log_dir')
log_file = c.get('logging', 'log_file')



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
    
#For COVID research
plotdir = '/run/aqnet/CO2-plot'
#plotfile = plotdir + '/aq.'+datetime.now().strftime('%Y%m%d_%H%M%S')+ socket.gethostname() +'.csv'
rundir = '/run/aqnet'
plotfile = '/run/aqnet/CO2-plot/CO2-plot.csv'
#savedir = '/var/log/wsn/CO2'
try:
    os.makedirs(plotdir)
except OSError:
    if not osp.isdir(rundir):
        raise
    
# COVID Create a unique filename
#import os
#savedir = '/var/log/aqnet/CO2'
#try:
#    os.makedirs(savedir)
#except OSError:
#    if not os.path.isdir(savedir):
#        raise
#localFile  = savedir+'/aq.'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.csv'


k30 = serial.Serial(serial_port, serial_baud)
k30.flushInput()
time.sleep(0.5)

def get_co2(device):
    device.flushInput()
    device.write('\xFE\x44\x00\x08\x02\x9F\x25')
    time.sleep(0.010)
    response = device.read(7)
    high, low = ord(response[3]), ord(response[4])
    return ((high << 8) | low)
    time.sleep(0.1)

fieldnames = ["Time", "CO2"]
#Starts at time 0 and increases every 10 seconds
seconds = 0
with open(plotfile, 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
while True:

    try:
        co2 = get_co2(k30)
        date = str(datetime.now())
        now = time.time()
        #time_seconds = str(datetime.now().strftime('%H:%M:%S.%f'))
        log.info('{:0.0f}'.format(co2))
        # for journlctl logs
        #print('{{"co2": {:0.0f}}}'.format(co2))

        #client.publish(report_topic,
        #               report.format(ts=now, co2=co2),
        #               qos=1, retain=True)
        
            

        with open(plotfile, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            info = {
            "Time": seconds,
            "CO2": co2,
        }

            csv_writer.writerow(info)
            print(seconds, co2)
            seconds += 2
            
        time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        k30.close()
        client.loop_stop()
        raise
    except:
        time.sleep(5)
        pass
