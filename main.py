
import time
import machine
import network
import ujson
from umqtt.simple import MQTTClient
import urandom


WIFI_NAME = b'your_wifi_name'
WIFI_PASSWORD = b'your_wifi_password'
THING_NAME = b'CatFeederThingESP32'
AWS_ENDPOINT = b'aws_iot_endpoint_url'



# AWS IoT Core publish topic
PUB_TOPIC = b'cat-feeder/states'
# AWS IoT Core subscribe  topic
SUB_TOPIC = b'cat-feeder/action'


# Reading Thing Private Key and Certificate into variables for later use
with open('/certs/key.der', 'rb') as f:
    DEV_KEY = f.read()
# Thing Certificate
with open('/certs/cert.der', 'rb') as f:
    DEV_CRT = f.read()



# Wifi Connection Setup
def wifi_connect():
    print('Connecting to wifi...')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_NAME, WIFI_PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    print('Connection details: %s' % str(wlan.ifconfig()))


# Callback function for all subscriptions
def mqtt_subscribe_callback(topic, msg):
    print("Received message from topic: %s message: %s" % (topic, msg))


def get_food_capacity():
    return urandom.randint(0, 100)


# Connect to wifi
wifi_connect()

# Set AWS IoT Core connection details
mqtt = MQTTClient(
    client_id=THING_NAME,
    server=AWS_ENDPOINT,
    port=8883,
    keepalive=5000,
    ssl=True,
    ssl_params={'key':DEV_KEY, 'cert':DEV_CRT, 'server_side':False})

# Establish connection to AWS IoT Core
mqtt.connect()

# Set callback for subscriptions
mqtt.set_callback(mqtt_subscribe_callback)

# Subscribe to topic
mqtt.subscribe(SUB_TOPIC)



while True:
    message = b'{"food_capacity":%s}' % get_food_capacity()
    print('Publishing message to topic %s message %s' % (PUB_TOPIC, message))
    mqtt.publish(topic=PUB_TOPIC, msg=message, qos=0)

    # Check subscriptions for message
    mqtt.check_msg()
    time.sleep(5)


