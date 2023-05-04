"""
HTTP, MQTT, WebSocket, etc.

"""

# Refer to...
# https://toomtamdn.medium.com/%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%87%E0%B8%B2%E0%B8%99-python-%E0%B8%A3%E0%B9%88%E0%B8%A7%E0%B8%A1%E0%B8%81%E0%B8%B1%E0%B8%9A-mqtt-aea8549045e1

import paho.mqtt.client as mqtt

from base.__NetworkBase import NetClient


class ClientMQTT(NetClient):
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__client = mqtt.Client()
        # self.__client.on_connect

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def client(self):
        return self.__client
