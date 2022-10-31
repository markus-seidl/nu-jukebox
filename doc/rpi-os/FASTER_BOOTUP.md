FROM https://singleboardbytes.com/637/how-to-fast-boot-raspberry-pi.htm


sudo nano /boot/config.txt

* disable_splash=1: This line disables the rainbow splash screen that appears on booting your Raspberry Pi OS. It is also present in other raspberry Linux distro.
* dtoverlay=disable-bt: This line disables Bluetooth connections in your system. Therefore, if your project utilizes Bluetooth, you shouldn’t add this.
* boot_delay=0: By default, this value is set to 1second if not specified.


sudo nano /boot/cmdline.txt

We will make the following edits:

delete the splash parameter
Add quiet parameter


systemd-analyze blame

systemctl disable cups



# Sonstiges

apt purge --remove plymouth
apt remove --purge x11-common
