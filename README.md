# mqtt-rpi-screen-brightness
This python script is designed to run as a service on a Raspberry Pi.  It subscribes to a given MQTT topic and sets the screen brightness based on that topic.  Works well when you want to use HA or another home automation tool to set the brightness of the screen.

## PI CONFIGURATION:
To control the RPi 7" touchscreen you need to edit the backlight rules. From a terminal window:
```
sudo nano /etc/udev/rules.d/backlight-permissions.rules
```

and add:
```
SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power"
```
Then reboot.

## INSTALLATION:
For the script to work properly, you need to install a few things first.  You'll need the module to control the brightness of the screen:
```
sudo pip3 install rpi-backlight
```

Since you'll be subscribing to an MQTT topic, you will also need the following:
```
sudo pip3 install paho-mqtt
```

It is recommended you install this in `/home/pi`.  The service file you'll install later assumes this, so if you install it somewhere else, you'll need to edit rpisc.service.

## CONFIGURATION:
You need to create a new file called `settings.py` in the `data` folder.  The `data` folder is created at first run, or you can create in manually.  You must at least include the `mqtt_topic` string in the settings file.  There are a number of other options available in the settings:

* `mqtt_host = <str>` (default `127.0.0.1`)  
The IP address of your MQTT broker (or HA instance depending on which notifier you use).

* `mqtt_port = <int>` (default `1883`)  
The port of your MQTT broker.

* `mqtt_user = <str>` (default `mqtt`)  
The username needed if authentication is required for your MQTT broker.

* `mqtt_pass = <str>` (default `mqtt_password`)  
The password needed if authentication is required for your MQTT broker.

* `mqtt_clientid = <str>` (default `lightsensor`)  
The client ID provided to the MQTT broker.

* `mqtt_qos = <int>` (default `1`)  
By default the script uses quality of service level 1 to talk to the broker.  You can change that here to `0` or `2`, but be aware that QOS 0 sometimes does not read retained messages.

* `logbackups = <int>` (default `1`)  
The number of days of logs to keep.

* `debug = <boolean>` (default `False`)  
For debugging you can get a more verbose log by setting this to True.

## USAGE: 
To run from the terminal (for testing): `python3 /home/pi/mqtt-rpi-screen-brightness/execute.py`  
To exit: CNTL-C

Running from the terminal is useful during initial testing, but once you know it's working the way you want, you should set it to autostart.  To do that you need to copy one of the two scripts to the systemd directory, change the permissions, and configure systemd.
```
sudo cp -R /home/pi/mqtt-rpi-screen-brightness/mqttrpiscreen.service.txt /lib/systemd/system/mqttrpiscreen.service
sudo chmod 644 /lib/systemd/system/mqttrpiscreen.service
sudo systemctl daemon-reload
sudo systemctl enable mqttrpiscreen.service
```

From now on the script will start automatically after a reboot.  If you want to manually stop or start the service you can do that as well. From a terminal window:
```
sudo systemctl stop mqttrpiscreen.service 
sudo systemctl start mqttrpiscreen.service 
```

If you change any settings, it's best to restart the service.

### USING WITH HOME ASSISTANT

You can use the `mqtt.publish` service to publish the desired screen brightness to the right topic.