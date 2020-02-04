#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of gotify-indicator
#
# Copyright (c) 2020 Lorenzo Carbonell Cerezo <a.k.a. atareao>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import websocket
import time
import requests
import threading
import json


class GotifyClient(threading.Thread):
    def __init__(self, https_protocol, base_url, application_name,
                 application_token, client_token, on_message, debug=False):
        threading.Thread.__init__(self)
        protocol = 'https' if https_protocol else 'http'
        ws_protocol = 'wss' if https_protocol else 'ws'
        self.url = '{}://{}'.format(protocol, base_url)
        self.wss_url = '{}://{}/stream'.format(ws_protocol, base_url)
        self.application_name = application_name
        self.application_token = application_token
        self.ws = websocket.WebSocketApp(self.wss_url,
                                         on_message=on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         header={"X-Gotify-Key":
                                                 client_token})
        if debug:
            websocket.enableTrace(True)
        self.running = False

    def run(self):
        self.running = True
        self.ws.run_forever()

    def close(self):
        self.ws.close()
        self.running = False

    def is_running(self):
        return self.running

    def on_message(self, message):
        print(message)
        message = json.loads(message)
        if self.application_name != message['title']:
            print(message['title'])
            print(message)

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("### closed ###")

    def get_health(self):
        headers = {'X-Gotify-Key': self.application_token}
        url = '{}/{}'.format(self.url, 'health')
        ans = requests.get(url, headers=headers)
        return ans.json()

    def send_message(self, message, title=None, priority=0):
        headers = {'X-Gotify-Key': self.application_token}
        json = {'message': message,
                'priority': priority}
        if title:
            json['title'] = title
        url = '{}/{}'.format(self.url, 'message')
        ans = requests.post(url, headers=headers, json=json)
        return ans.json()


if __name__ == "__main__":
    import time
    from configurator import Configuration
    configuration = Configuration()
    preferences = configuration.get('preferences')

    https_protocol = preferences['https_protocol']
    base_url = preferences['base_url']
    application_name = preferences['application_name']
    application_token = preferences['application_token']
    client_token = preferences['client_token']

    def on_message(ws, message):
        print(message)

    try:
        gc = GotifyClient(https_protocol,
                          base_url,
                          application_name,
                          application_token,
                          client_token,
                          on_message,
                          True)
        print(gc.get_health())
        gc.start()
        while True:
            time.sleep(5)
            gc.send_message("Ejemplo")
    except KeyboardInterrupt as e:
        gc.close()
        print(e)
