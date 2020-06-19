#!/bin/bash
#
# WSU Air Quality Network Sensor Prototype
# Laboratory for Atmospheric Research
# Washington State University


echo "Installing WSU AQN prototype..."

### SYSTEM CONF

#echo "Generating unique hostname..."
#SERIAL="$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2)"
#HOSTNAME="aqnetproto-$SERIAL"
#echo "Setting hostname to $HOSTNAME..."
#hostnamectl set-hostname $HOSTNAME
#echo "Finished updating hostname."

echo "Installing network configuration..."
cp etc/network/interfaces /etc/network/
echo "Finished setting up network. Changes take effect on reboot."

### SERVICES SETUP

mkdir -p /etc/wsn

# CO2 logger service
echo "Installing K30 logging service executable..."
cp bin/COVID-k30-logger.py /usr/sbin/COVID-k30-logger
chmod +x /usr/sbin/COVID-k30-logger
cp etc/wsn/COVID-k30-logger.conf /etc/wsn/

echo "Registering K30 logging service..."
cp etc/systemd/system/COVID-k30-logger.service /etc/systemd/system/

echo "Enabling K30 logging service start at boot..."
systemctl enable COVID-k30-logger.service

systemctl daemon-reload
echo "Starting K30 logging service..."
systemctl restart COVID-k30-logger.service