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
import gzip
import json
from mitmproxy import http

class SpoofHotfix:

    def __init__(self):

        # Various bits of data
        self.mtimes = {}
        self.mod_data = {}
        self.to_load = []
        self.next_prefix = 0
        self.modlist_pathname = 'injectdata/modlist.txt'
        self.base_hotfixes_file = '/home/pez/git/b2patching/bl3hotfixes/point_in_time/hotfixes_2020_06_11_-_16_10_03_-_guardian_takedown.json'
        with open(self.base_hotfixes_file) as df:
            # Do a little dance here to un-prettify the JSON, since I save it in a more
            # human-friendly format on disk.
            base_hotfixes = json.load(df)
            self.base_hotfixes = json.dumps(base_hotfixes, separators=(',', ':'))

    def load_modlist(self):
        cur_mtime = os.path.getmtime(self.modlist_pathname)
        if self.modlist_pathname in self.mtimes and self.mtimes[self.modlist_pathname] == cur_mtime:
            return
        print('Updating mod list...')
        self.mtimes[self.modlist_pathname] = cur_mtime
        self.to_load = []

        with open(self.modlist_pathname) as df:
            for line in df:
                line = line.strip()
                if line == '':
                    continue
                if line[0] == '#':
                    continue

                if line[0] == '/':
                    mod_path = '{}.txt'.format(line)
                else:
                    mod_path = 'injectdata/{}.txt'.format(line)
                if os.path.exists(mod_path):
                    self.to_load.append(mod_path)
                else:
                    print('WARNING: {} not found'.format(mod_path))

        print('Set {} mod(s) to load'.format(len(self.to_load)))

    def process_mod(self, pathname):

        # Make sure the mod file exists, and fail gracefully rather than allowing
        # an exception
        if not os.path.exists(pathname):
            if pathname in self.mtimes:
                del self.mtimes[pathname]
            print('WARNING: {} not found'.format(pathname))
            return []

        # Now continue on
        hf_counter = 0
        cur_mtime = os.path.getmtime(pathname)
        if pathname in self.mtimes and self.mtimes[pathname] == cur_mtime:
            return self.mod_data[pathname]
        print('Processing {}'.format(pathname))
        self.mtimes[pathname] = cur_mtime
        statements = []

        # We're generating our own prefixes now.  Just start at 0 and keep adding 1,
        # encoding as hex.  (I'd like to actually encode in base 36 or whatever, but
        # I don't care enough to implement that.)
        prefix = '{:X}'.format(self.next_prefix)
        self.next_prefix += 1

        # Read the file
        with open(pathname) as df:
            for line in df:
                line = line.strip()
                if line == '':
                    continue
                if line[0] == '#':
                    continue

                # Process the hotfix
                hf_counter += 1
                try:
                    (hftype, hf) = line.split(',', 1)
                except ValueError as e:
                    print('ERROR: Line could not be processed as hotfix, aborting this mod: {}'.format(line))
                    return []
                statements.append('{{"key":"{}-Apoc{}-{}","value":"{}"}}'.format(
                    hftype,
                    prefix,
                    hf_counter,
                    hf.replace('"', '\\"'),
                    ))

        self.mod_data[pathname] = statements
        return statements

    def request(self, flow):
        if flow.request.path.startswith('/v2/client/'):

            # Initial "authentication" request
            if flow.request.path.endswith('/pc/oak/authentication'):
                with open('spoof_data/authentication_response.json') as df:
                    flow.response = http.HTTPResponse.make(
                            200,
                            df.read().encode('utf8'),
                            {'Content-Type': 'application/json; charset=utf-8'},
                            )

            # Now the "verification" request (this is what sends the hotfixes, among other service info)
            elif flow.request.path.endswith('/pc/oak/verification'):

                with open('spoof_data/verification_response.json') as df:

                    cur_data = df.read().strip()

                    # Make sure that the data we read is primed to accept a new Micropatch stanza at
                    # the end
                    assert(cur_data.endswith(']}'))

                    self.load_modlist()
                    statements = ['']
                    for pathname in self.to_load:
                        statements.extend(self.process_mod(pathname))
                    if len(statements) > 1:
                        to_inject = ','.join(statements)
                    else:
                        to_inject = ''
                    cur_data = '{},{}{}{}{}'.format(
                            cur_data[:-2],
                            self.base_hotfixes[:-2],
                            to_inject,
                            self.base_hotfixes[-2:],
                            cur_data[-2:],
                            )
                    flow.response = http.HTTPResponse.make(
                            200,
                            # Looks like mitmproxy will automatically do the compression for us, I guess?
                            # If I manually gzip, it ends up double-gzipped.
                            cur_data.encode('utf8'),
                            #gzip.compress(cur_data.encode('utf8')),
                            {
                                'Content-Encoding': 'gzip',
                                'Content-Type': 'application/json; charset=utf-8',
                                },
                            )

addons = [
    SpoofHotfix()
    ]
