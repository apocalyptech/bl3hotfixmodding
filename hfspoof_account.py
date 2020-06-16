#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright 2019 Christopher J. Kucera
# <cj@apocalyptech.com>
# <http://apocalyptech.com/contact.php>
#
# Borderlands 3 Hotfix Injector is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Borderlands 3 Hotfix Injector is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Borderlands 3 Hotfix Injector.  If not, see
# <https://www.gnu.org/licenses/>.

import os
import uuid
import json
import datetime
from mitmproxy import http

class SpoofHotfix:

    def __init__(self):

        # Various bits of data
        self.mtimes = {}
        self.pages = {}
        self.uuid = uuid.uuid4()
        initial_data = {
                'archway': {
                    'in_progress': True,
                    'request_id': str(self.uuid),
                    },
                'messages': [],
                'success': True,
                }
        self.initial_response = json.dumps(initial_data, separators=(',', ':')).encode('utf8')
        print('Started with request UUID of: {}'.format(self.uuid))

    def log_msg(self, message):
        print('{} - {}'.format(datetime.datetime.now(), message))

    def get_page(self, path):
        cur_mtime = os.path.getmtime(path)
        if path not in self.mtimes or self.mtimes[path] != cur_mtime:
            print('Reading page: {}'.format(path))
            with open(path) as df:
                self.pages[path] = df.read().encode('utf8')
                self.mtimes[path] = cur_mtime
        return self.pages[path]

    def request(self, flow):

        # A redirect happens here, I guess...
        if flow.request.path == '/' or flow.request.path == '':
            self.log_msg('Handling redirect to shift')
            flow.response = http.HTTPResponse.make(
                    301,
                    self.get_page('spoof_data/account_redir.html'),
                    {'Location': 'https://shift.gearboxsoftware.com'},
                    )

        # Initial auth post
        elif flow.request.path.startswith('/v1/auth/oak/pc/'):
            self.log_msg('Handling initial auth post')
            flow.response = http.HTTPResponse.make(
                    200,
                    self.initial_response,
                    {'Content-Type': 'application/json; charset=utf-8'},
                    )

        # Now some kind of followup request
        elif flow.request.path.startswith('/v1/verify/oak/pc/'):
            self.log_msg('Handling auth followup request')
            flow.response = http.HTTPResponse.make(
                    200,
                    # Data in here's been all randomized
                    self.get_page('spoof_data/account_other.json'),
                    {'Content-Type': 'application/json; charset=utf-8'},
                    )

        # Unknown?
        else:
            self.log_msg('Passing through unknown URL: {}'.format(flow.request.path))

addons = [
    SpoofHotfix()
    ]
