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
echo "Installing K30 logging and plotting service executable..."

cp bin/COVID-k30-logger.py /usr/sbin/COVID-k30-logger
chmod +x /usr/sbin/COVID-k30-logger

cp etc/wsn/COVID-k30-logger.conf /etc/wsn/

cp bin/COVID-k30-logger-plot.py /usr/sbin/COVID-k30-logger-plot
chmod +x /usr/sbin/COVID-k30-logger-plot

cp bin/k30-plotter.py /usr/sbin/k30-plotter
chmod +x /usr/sbin/k30-plotter

echo "Registering K30 logging service..."
cp etc/systemd/system/COVID-k30-logger.service /etc/systemd/system/
cp etc/systemd/system/COVID-k30-logger-plot.service /etc/systemd/system/
cp etc/systemd/system/k30-plotter.service /etc/systemd/system/

echo "Enabling K30 logging service start at boot..."
systemctl enable COVID-k30-logger.service
systemctl enable COVID-k30-logger-plot.service
systemctl enable k30-plotter.service

systemctl daemon-reload
echo "Starting K30 logging service..."
systemctl restart COVID-k30-logger.service
systemctl restart COVID-k30-logger-plot.service
systemctl restart k30-plotter.service