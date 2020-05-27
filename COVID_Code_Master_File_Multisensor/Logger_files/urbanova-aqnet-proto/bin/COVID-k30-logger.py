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

import serial
import socket
#import paho.mqtt.client as paho

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
try:
    os.makedirs(rundir)
except OSError:
    if not osp.isdir(rundir):
        raise
    
#For COVID research
savedir = '/var/log/wsn/CO2'
savefile = savedir + '/aq.'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.csv'

try:
    os.makedirs(savedir)
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

while True:
    try:
        co2 = get_co2(k30)
        date = str(datetime.now())
        now = time.time()
        log.info('{:0.0f}'.format(co2))

        # for journlctl logs
        print('{{"co2": {:0.0f}}}'.format(co2))

        # for Itron Riva
        with open(runfile, 'a+') as f:
            f.write(date + ',' + socket.gethostname() + ',' + str(co2))
	    f.write('\n')

        #client.publish(report_topic,
        #               report.format(ts=now, co2=co2),
        #               qos=1, retain=True)

        with open(savefile, 'a+') as f:
            f.write(str(datetime.now()) + ', ' + str(co2))
	    f.write('\n')


        time.sleep(interval)
    except (KeyboardInterrupt, SystemExit):
        k30.close()
        client.loop_stop()
        raise
    except:
        time.sleep(5)
        pass
