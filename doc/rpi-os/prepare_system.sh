#!/usr/bin/env bash

SYSTEMD_USR_PATH="/usr/lib/systemd/user/"
SYSTEMD_PATH="/lib/systemd/system/"

echo " * Install needed packages and update the system"
sudo apt update
sudo apt upgrade
sudo apt install portaudio19-dev python3-pyaudio ffmpeg libavcodec-extra git

echo " * Register nu-jukebox as daemon and enable it"
sudo cp -f "nu-jukebox-daemon.service" "${SYSTEMD_PATH}"
sudo chmod 644 "${SYSTEMD_PATH}/nu-jukebox-daemon.service"

#systemctl --user daemon-reload
#systemctl --user enable nu-jukebox-daemon.service
sudo systemctl daemon-reload
sudo systemctl enable nu-jukebox-daemon

echo " * Enable SPI"
sudo raspi-config nonint do_spi 0

# FROM https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/f56c36978ac1f5219ebdc1a51bd62fe53edb8ae0/installation/routines/optimize_boot_time.sh
echo "  * Disable keyboard-setup.service"
sudo systemctl disable keyboard-setup.service

echo "  * Disable triggerhappy.service"
sudo systemctl disable triggerhappy.service
sudo systemctl disable triggerhappy.socket

echo "  * Disable raspi-config.service"
sudo systemctl disable raspi-config.service

echo "  * Disable apt-daily.service & apt-daily-upgrade.service"
sudo systemctl disable apt-daily.service
sudo systemctl disable apt-daily-upgrade.service
sudo systemctl disable apt-daily.timer
sudo systemctl disable apt-daily-upgrade.timer

echo "  * Disable hciuart.service and bluetooth"
sudo systemctl disable hciuart.service
sudo systemctl disable bluetooth.service

# systemctl disable cups

echo " * Install python libraries"
sudo pip install -r requirements.txt

echo " * Make system read only"
# https://medium.com/@andreas.schallwig/make-your-raspberry-pi-file-system-read-only-raspbian-buster-c558694de79
# sudo logread

sudo apt remove --purge triggerhappy logrotate dphys-swapfile
sudo apt autoremove --purge
sudo apt install busybox-syslogd
sudo apt remove --purge rsyslog


