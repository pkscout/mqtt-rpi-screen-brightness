import resources.config as config
from resources.lib.screens import RPiTouchscreen
from resources.lib.xlogger import Logger
import os
import time
from paho.mqtt import client as mqtt_client
from paho.mqtt import subscribe as mqtt_subscribe

try:
    import sdnotify
    has_notify = True
except ImportError:
    has_notify = False


class Main:

    def __init__(self, thepath):
        self.LW = Logger(logfile=os.path.join(os.path.dirname(thepath), 'data', 'logs', 'logfile.log'),
                         numbackups=config.Get('logbackups'), logdebug=config.Get('debug'))
        self.LW.log(['script started, debug set to %s' %
                    str(config.Get('debug'))], 'info')
        self.SCREEN = self._pick_screen()
        client = self._connect_mqtt()
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            pass
        self.LW.log(['setting brightness to 100 and closing down'], 'info')
        self._set_brightness(100)

    def _connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.LW.log(["Connected to MQTT Broker!"])
            else:
                self.LW.log(["Failed to connect, return code %d\n", rc])
            self._subscribe(client)
        client = mqtt_client.Client(config.Get('mqtt_clientid'))
        client.username_pw_set(config.Get('mqtt_user'),
                               config.Get('mqtt_pass'))
        client.on_connect = on_connect
        success = False
        while not success:
            try:
                success = True
                client.connect(config.Get('mqtt_host'),
                               config.Get('mqtt_port'))
            except OSError:
                success = False
                self.LW.log([
                    'Failed to connect due to network issue, trying again in 5 seconds'])
                time.sleep(5)
        return client

    def _subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            payload = msg.payload.decode()
            self.LW.log(['Received %s from %s' % (payload, msg.topic)])
            self._set_brightness(payload)
        client.subscribe(config.Get('mqtt_topic'))
        client.on_message = on_message

    def _pick_screen(self):
        return RPiTouchscreen(testmode=config.Get('testmode'))

    def _set_brightness(self, payload):
        try:
            brightness = int(payload)
        except ValueError:
            brightness = 100
            self.LW.log(
                ['Error setting %s to int, setting brightness to 100' % str(payload)])
        self.LW.log(['Setting brightness to %s' % str(brightness)])
        self.SCREEN.SetBrightness(brightness=brightness)
