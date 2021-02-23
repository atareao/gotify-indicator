#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of gotify-indicator
#
# Copyright (c) 2021 Felix Nüsse
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

from configurator import Configuration
from config import CACHE_DIR
import requests
import threading
import shutil


class Cache(threading.Thread):

    def __init__(self, https_protocol, base_url, client_token):
        threading.Thread.__init__(self)
        protocol = 'https' if https_protocol else 'http'
        self.url = '{}://{}'.format(protocol, base_url)
        self.client_token = client_token

    def startCaching(self):
        headers = {'X-Gotify-Key': self.client_token}
        url = '{}/{}'.format(self.url, 'application')
        ans = requests.get(url, headers=headers)
        for app in ans.json():
            imageurl = '{}/{}'.format(self.url, app['image'])
            self.storeImage(imageurl, app['id'])
        return ans.json()

    def storeImage(self, imageurl, id):
        image = requests.get(imageurl, stream=True)

        image.raw.decode_content = True
        with open(CACHE_DIR + str(id), 'wb') as target:
            shutil.copyfileobj(image.raw, target)
            print("written to: " + CACHE_DIR + str(id))

    def instanciate(self):
        configuration = Configuration()
        preferences = configuration.get('preferences')

        https_protocol = preferences['https_protocol']
        base_url = preferences['base_url']
        client_token = preferences['client_token']
        cachepath = preferences['client_token']

        cache = Cache(https_protocol,
                      base_url,
                      client_token)

        cache.startCaching()
