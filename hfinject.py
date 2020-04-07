#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright 2019 Christopher J. Kucera
# <cj@apocalyptech.com>
# <http://apocalyptech.com/contact.php>
#
# Borderlands ModCabinet Sorter is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Borderlands ModCabinet Sorter is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Borderlands ModCabinet Sorter.  If not, see
# <https://www.gnu.org/licenses/>.

import os
import gzip

class InjectHotfix:

    def __init__(self):

        # Various bits of data
        self.mtimes = {}
        self.mod_data = {}
        self.to_load = []
        self.modlist_pathname = 'injectdata/modlist.txt'

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

        prefix = None
        with open(pathname) as df:
            for line in df:
                line = line.strip()
                if line == '':
                    continue
                if line[0] == '#':
                    continue

                # Check for prefix
                if not prefix:
                    if line.lower().startswith('prefix:'):
                        prefix = line.split(':', 1)[1].strip()
                    else:
                        print('WARNING: no prefix found for {}'.format(pathname))
                        self.mod_data[pathname] = []
                        self.mtimes[pathname] = 0
                        return
                else:
                    hf_counter += 1
                    (hftype, hf) = line.split(',', 1)
                    statements.append('{{"key":"{}-Apoc{}{}","value":"{}"}}'.format(
                        hftype,
                        prefix,
                        hf_counter,
                        hf.replace('"', '\\"'),
                        ))

        self.mod_data[pathname] = statements
        return statements

    def response(self, flow):
        if flow.request.path == '/v2/client/epic/pc/oak/verification':

            gzipped = False
            if 'Content-Encoding' in flow.response.headers and flow.response.headers['Content-Encoding'] == 'gzip':
                raw_data = gzip.decompress(flow.response.data.content)
                gzipped = True
            else:
                raw_data = flow.response.data.content

            cur_data = raw_data.decode('utf8')
            if cur_data.endswith(']}]}'):
                self.load_modlist()
                statements = ['']
                for pathname in self.to_load:
                    statements.extend(self.process_mod(pathname))
                if len(statements) > 1:
                    to_inject = ','.join(statements)
                else:
                    to_inject = ''
                cur_data = '{}{}{}'.format(
                        cur_data[:-4],
                        to_inject,
                        cur_data[-4:],
                        )
                if gzipped:
                    flow.response.data.content = gzip.compress(cur_data.encode('utf8'))
                else:
                    flow.response.data.content = cur_data.encode('utf8')
                #if 'Content-Length' in flow.response.headers:
                #    # This isn't actually the case for GBX
                #    flow.response.headers['Content-Length'] = str(len(flow.response.data.content))

addons = [
    InjectHotfix()
    ]
