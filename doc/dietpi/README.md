
# Install

## OS

* Install DietPi
  * Disable UART
  * Enable Audio (install alsa-utils)
  * Select new password for everything (you can use the same, but don't use the default dietpi one)
  * Do not install anything else, select ok to install a pure minimal OS
* Reboot DietPi
* Analyze
  * Check `systemd-analyze blame` if there is any service left that needs to be removed.
    * Wifi is usually ok, even if it needs long to initialize, as the jukebox service can start earlier or in parallel

## Jukebox

* `apt update && apt install python3 ffmpeg python3-pip build-essential python3-dev libasound2-dev portaudio19-dev python3-pyaudio -y`
* Upload the files under `/root/nu-jukebox/`
* `pip3 install -r requirements.txt`
* 
