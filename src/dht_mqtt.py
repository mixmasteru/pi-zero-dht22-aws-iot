#!/usr/bin/env python

from __future__ import print_function
import time
import json
import traceback
from config import *
from sensor.DHT22 import DHT22
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from retrying import retry

sleeps = 600
intv = 600

myAWSIoTMQTTClient = AWSIoTMQTTClient(device_name)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(root_crt, key, cert)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

print("Start\n")
# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
print("connected\n")
# myAWSIoTMQTTClient.subscribe("sdk/test/Python", 1, customCallback)
# time.sleep(2)
last_time = 0
dht = DHT22(gpio)


@retry(wait_exponential_multiplier=1000, wait_exponential_max=30000, stop_max_delay=300000)
def publish(topic, payload):
    t = time.localtime(time.time())
    print("sending "+str(payload)+" to "+topic+" "+time.strftime("%d-%m-%Y %H:%M:%S", t))
    myAWSIoTMQTTClient.publish(topic, json.dumps(payload), 1)


try:
    # Publish to the same topic in a loop forever
    while True:
        try:
            done = dht.read_sensor()
            if done:
                now = time.time()
                localtime = time.localtime(now)

                if (last_time+intv) <= now:
                    payload = dht.format_payload('temp', now, dht.temperature)
                    publish(topic_temp, payload)
                    payload = dht.format_payload('hum', now, dht.humidity)
                    publish(topic_hum, payload)
                    last_time = now
            else:
                print("no data from sensor")
            time.sleep(sleeps)
        except Exception:
            print("--------------------")
            traceback.print_exc()
            raise Exception

except KeyboardInterrupt:
    print('Exit')
