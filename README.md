# Sensor Setup and Configuration Steps
This repository contains code written for the Air Quality Sensor network with the purpose of collecting CO2 and PM data to monitor COVID-19 virus particles in the classroom.

### COVID_Code_Master_File 
This folder contains the code to automatically configure the K30 CO2 sensor and have it log CO2 data to /var/log/wsn on start up. Follow the steps below to configure it (the setup is for all the sensors; if only using the CO2 sensors then ignore the others):

### Components

* Single-board computer (Raspberry Pi 3 - Model B)
    <https://www.adafruit.com/product/3055>
* TPU sensor (BME280 breakout; Adafruit)
    <https://www.adafruit.com/product/2652>
* CO2 sensor (K-30; CO2Meter.com)
    <https://www.co2meter.com/products/k-30-co2-sensor-module>
* Particulate sensor (OPC-N2; Alphasense)
    <http://www.alphasense.com/index.php/products/optical-particle-counter/>

### Assembly

Connect all the sensors directly to the Pi. Do not use a separate power supply
for the OPC-N2 (in contradiction to the software repo readme).

> Through trial-and-error, it is determined that the OPC-N2 exhibits a high
> sensitivity to input voltage and grounding differentials between its data
> and power lines. To avoid the dreaded "your firmware could not be detected"
> error, ensure that both power input and power ground lines are completely
> tied to the Pi Zero's 5V and G rails, respectively. 
>
> In practice, the Pi can source 1.5A through it's 5V GPIO pins. You are
> therefore advised to power the OPC-N2 through the Pi. 

#### Enabling wifi on the WSU Wireless Network

1. Copy and paste the wpa_supplicant.conf file from the current directory to /etc/wpa_supplicant/ using the command "sudo cp" followed by the appropriate directory.
Alternatively, use the command "sudo pcmanfm" and manually copy and paste the file to the /etc/wpa_supplicant/ directory.For 
security reasons please email Kristian Gubsch (gubschk@gmail.com) for the supplicant file or navigate to the /etc/wpa_supplicant directory on another Pi to obtain the 
wifi credentials.

2. Run the command "sudo reboot" 

### Initial Setup

1. Purchase a 128-GB Sandisk Ultra microSDXC UHS-1 memory card (with adapter).

2. Download the last version of the Jessie operating system for the Raspberry Pi computer at:
       http://downloads.raspberrypi.org/raspbian/images/raspbian-2017-07-05/2017-07-05-raspbian-jessie.zip

3. Install the Jessie operating system on the memory card using the instructions at:
       https://www.raspberrypi.org/documentation/installation/installing-images/README.md

   Note that these instructions depend on what type of computer you are using (Windows, Mac, Linux).

4. With `raspi-config`:
    1. Change the password. Used the lab password and appended X, where X is the rooftop unit number.
    2. Set approp locale/kb/tz
    3. ~~Set the hostname to `airqualityX`~~, where X is the rooftop unit number. 
            Will set later using Pi's serial number
    4. Enable SPI
    5. Enable I2C
    6. Disable shell on serial port, but keep the serial port hardware enabled.
    7. Enable SSH server
    8. Disable wait for network at boot
    9. Choose to "Update" in raspi-config
5. Reboot
6. `sudo apt-get dist-upgrade`
7. Install basic utilities:
    `sudo apt-get install tux`
    `sudo apt-get install htop`
    `sudo apt-get install build-essential`  (Might already be up-to-date.)
    `sudo apt-get install python-dev`



8. Enable NPT stats: edit `/etc/ntp.conf` to uncomment line starting
    with `statsdir /var/log/ntpstats/`

9. Setup watchdog service
    1. install watchdog timer using `sudo apt-get install watchdog`
    2. edit `/boot/config.txt` to contain `dtoverlay=watchdog=on`
       [ref](https://github.com/raspberrypi/linux/issues/1285#issuecomment-182264729)
    3. fixup the systemd service file [thanks to](https://kd8twg.net/2015/10/30/raspberry-pi-enabling-watchdog-on-raspbian-jessie/):
       edit `/lib/systemd/system/watchdog.service` to contain:

        ```
        [Install]
        WantedBy=multi-user.target
        ```

    4. edit `/etc/watchdog.conf` to contain
       [ref](https://blog.kmp.or.at/watchdog-for-raspberry-pi/)

        ```
        watchdog-device = /dev/watchdog
        watchdog-timeout = 10
        interval = 2
        max-load-1 = 24
        ```

    5. enable service and start it using sytemctl
        `sudo systemctl enable watchdog`
        `sudo systemctl start watchdog`
        
    6. finally, test it with a fork bomb: `:(){ :|:& };:`
       the Pi should return a PID number, then hang, then reboot

10. Enable persistent system logs: `sudo mkdir -p /var/log/journal`
    [ref](https://www.digitalocean.com/community/tutorials/how-to-use-journalctl-to-view-and-manipulate-systemd-logs)

11. Download supporting packages for various sensors
    1. install `python-pip`
    2. `pip install spidev`
    3. `mkdir aqnet/software/`   (Patrick, note that this directory could be renamed to something more appropriate.)
    4. `cd aqnet/software`
    3. `git clone https://github.com/raspberrypi/weather-station`
    4. `git clone https://github.com/dhhagan/py-opc.git`
    5. `git clone https://github.com/adafruit/Adafruit_Python_GPIO`
    6. `git clone https://github.com/adafruit/Adafruit_Python_BME280`
    7. `cd Adafruit_Python_GPIO && sudo python setup.py install`
    8. `cd ..`
    9. `cd Adafruit_Python_BME280 && sudo python setup.py install`
    10. `cd ..`
    11. `cd py-opc && sudo python setup.py install`
    12. `sudo apt-get install python-pandas`
    
    
### VNC Configuration

### VNC
1. Run the commands "sudo apt-get update" and "sudo apt-get upgrade"
2. Install the VNC server with sudo apt-get install tightvncserver
3. Set up and run the server by running the command "vncserver :1"
4. To start the software automatically, run the command "sudo nano /etc/rc.local" and before the "exit 0" line, enter the code "su - pi -c '/usr/bin/vncserver :1'"
5. Restart the Pi with "sudo reboot"
6. Confirm the vnc server is running with the command "vncserver :1" and it should say "A vnc server is already running"
7. Enter IP address in VNC viewer program
The password for all VNC servers is lar2020

### Enabling copy/paste from remote to local machine (https://www.youtube.com/watch?v=npiX-11kBUU)
	
1. Run the command "sudo apt-get install autocutsel"
2. Edit the xstartup file with the command "nano /home/pi/.vnc/xstartup"
3. Type the words "autocutsel -fork" right beneath the words "xsetroot -solid grey"
4. Restart the Raspberry Pi to enable copy/paste

#### Enabling plotting over Matplotlib to the VNCserver 

1. Use the command "xhost +localHost"

### COVID_Code_Master_File_k30plotting
This folder contains the code to configure the CO2 sensor and have it plot data in real time. Follow the steps below to configure the sensors and have them automatically log data to /var/log/wsn and run/aqnet/CO2_plot on boot.

### CO2 sensor Configuration
1. Open a Linux terminal on the Raspberry Pi
2. Navigate to /home/pi/Documents/COVID_Code_Master_File_k30plotting/Logger_files/urbanova-aqnet-proto directory in the terminal
3. Run the command "sudo sh COVID-install-plotting.sh"
4. Navigate to /var/log/wsn to ensure the CO2 sensor is logging. A new file with the current timestamp should have appeared in this directory

### CO2 Sensor realtime plotting
1. Open a Linux terminal and navigate to the /home/pi/Documents/COVID_Code_Master_File_k30plotting/Logger_files/urbanova-aqnet-proto directory/bin directory. 
2. Run the commmand "xhost +localHost" to enable viewing on the VNC client.
3. Run the command "sudo python k30-plotter.py" and a real time plot of CO2 data should appear on the screen.


