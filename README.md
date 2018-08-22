Mic Array
=========

Utils for [ReSpeaker Microphone Array](https://www.seeedstudio.com/ReSpeaker-Mic-Array-Far-field-w--7-PDM-Microphones--p-2719.html). It includes DOA (Direction of Arrival), VAD (Voice Activity Detection), KWS (Keyword Spotting or Keyword Search) and etc.

+ `pixel_ring.py` - control the pixel ring
+ `mic_array.py` - read 8 channels raw audio from the Mic Array and estimate sound's DOA (Direction of Arrival)
+ `vad_doa.py` - do VAD (Voice Activity Detection) and then estimate DOA
+ `kws_doa.py` - search keyword and then estimate DOA

## Requirements
+ For ReSpeaker USB Mic Array - Far-field w/ 7 PDM Microphones

  Change the Mic Array's firmware to get 8 channels raw audio. See https://github.com/respeaker/mic_array_dfu

+ For 4 Mic Array Pi hat

   Install [seeed-voicecard](https://github.com/respeaker/seeed-voicecard) driver first. Change `CHANNELS = 8` to `CHANNELS = 4` in [vad_doa.py](https://github.com/respeaker/mic_array/blob/master/vad_doa.py#L10) and [kws_doa.py](https://github.com/respeaker/mic_array/blob/master/kws_doa.py#L11)

## Get started
1. Run `pixel_ring.py` to control the pixel ring of the Mic Array through USB HID

   ```
   sudo pip install pyusb
   sudo python pixel_ring.py
   ```
   If you don't want to access USB device with `sudo`, add a udev `.rules` file to `/etc/udev/rules.d`:
   ```
   echo 'SUBSYSTEM=="usb", MODE="0666"' | sudo tee -a /etc/udev/rules.d/60-usb.rules
   sudo udevadm control -R  # then re-plug the usb device
   ```

2. Read 8 channels audio from the Mic Array and estimate sound's DOA
   ```
   sudo apt-get install python-numpy    # or pip install numpy
   python mic_array.py
   ```

3. Do VAD and then estimate DOA
   ```
   sudo pip install webrtcvad
   python vad_doa.py
   ```

4. Do KWS and then estimate DOA

   Get snowboy work and run `python kws_doa.py`
   ```
   git submodule init
   git submodule update
   cd snowboy/swig/Python
   sudo apt-get install python-dev libatlas-base-dev swig           # requiremetns to compile snowboy
   make                                                 # if got an error of swig3.x.x, edit the Makefile and disable the swig version check.
   echo 'from snowboydetect import *' > __init__.py     # create __init__.py for a python module
   cd ../../..                                          # chang to the root directory of the repository
   ln -s snowboy/swig/Python snowboydetect
   python kws_doa.py
   ```

## For Raspberry Pi
Google released [Google Assistant Library](https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library) for Raspberry Pi to provide hotword detection ("Ok Google" or "Hey Google"), audio recording, assistant response playback and etc. We can add LED lights indicator based on the library to make a device very similar with Google Home.

1. Follow [the guide](https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library) to install Google Assistant Library.
2. Run `python google_assistant_for_raspberry_pi.py`

## Use 4 Mic Array with ODAS to sound source localization and tracking
[ODAS](https://github.com/introlab/odas) is a very cool project to perform sound source localization, tracking, separation and post-filtering. Let's have a try!

1. get ODAS and build it

```
sudo apt-get install libfftw3-dev libconfig-dev libasound2-dev
git clone https://github.com/introlab/odas.git --branch=phoenix
mkdir odas/build
cd odas/build
cmake ..
make
```

2. get ODAS Studio from https://github.com/introlab/odas_web/releases and open it. You can run ODAS Studio on a computer or the Raspberry Pi

The `odascore` will be at `odas/bin/odascore`, the config file is at [odas.cfg](odas.cfg). Change `odas.cfg` based on your sound card number.


```
    interface: {
        type = "soundcard";
        card = 1;
        device = 0;
    }
```

If you run the ODAS Studio on a computer, you should also need to change IP address from `127.0.0.1` to the IP of the computer.


![](https://github.com/introlab/odas_web/raw/master/screenshots/live_data.png)


