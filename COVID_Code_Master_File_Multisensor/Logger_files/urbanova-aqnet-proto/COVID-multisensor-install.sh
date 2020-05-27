#!/bin/bash
#
# WSU Air Quality Network Sensor Prototype
# Laboratory for Atmospheric Research
# Washington State University


echo "Installing WSU AQN prototype..."

### SYSTEM CONF

echo "Installing network configuration..."
cp etc/network/interfaces /etc/network/
echo "Finished setting up network. Changes take effect on reboot."

### SERVICES SETUP

mkdir -p /etc/wsn

# Multisensor logger service
echo "Installing multisensor logging service executable..."
cp bin/multisensor-logger.py /usr/sbin/multisensor-logger
chmod +x /usr/sbin/multisensor-logger
#cp etc/wsn/multisensor-logger.conf /etc/wsn/

echo "Registering multisensor logging service..."
cp etc/systemd/system/multisensor-logger.service /etc/systemd/system/

echo "Enabling multisensor logging service start at boot..."
systemctl enable multisensor-logger.service

systemctl daemon-reload
echo "Starting Multisensor logging service..."
systemctl restart multisensor-logger.service

