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
import sys
import gzip
import configparser

class InjectHotfix:

    def __init__(self):

        # Various bits of data
        self.mtimes = {}
        self.file_includes = set()
        self.mod_data = {}
        self.to_load = []
        self.next_prefix = 0
        self.mod_dir = None
        self.modlist_pathname = None
        self.initialized = False

        # This happens if you're running mitmproxy via docker -- do a chdir to get to
        # where we're supposed to be, in that case.
        if os.getcwd() == '/':
            os.chdir(os.path.dirname(os.path.realpath(__file__)))

        # Create a default `hfinject.ini` if it doesn't already exist
        if not os.path.exists('hfinject.ini'):
            config = configparser.ConfigParser()
            config['main'] = {'ModDir': 'injectdata'}
            try:
                with open('hfinject.ini', 'w') as df:
                    config.write(df)
                print('-'*80)
                print('NOTICE: hfinject.ini created with the default values.  Look it over to make')
                print('sure that you\'re happy with the default mod location!')
                print('')
                print('File contents:')
                print('')
                with open('hfinject.ini') as df:
                    sys.stdout.write(df.read())
                print('-'*80)
            except Exception as e:
                print('-'*80)
                print('ERROR: Could not write out example hfinject.ini file!')
                print('-'*80)
                return

        # Now read in the ini file
        config = configparser.ConfigParser()
        config.read('hfinject.ini')
        if 'main' in config and 'ModDir' in config['main']:
            self.mod_dir = config['main']['ModDir']
            self.modlist_pathname = os.path.join(self.mod_dir, 'modlist.txt')
            if os.path.exists(self.modlist_pathname):
                self.initialized = True
                print('-'*80)
                print('Initialized with mod directory: {}'.format(self.mod_dir))
                print('Path to modlist.txt: {}'.format(self.modlist_pathname))
                print('-'*80)
            else:
                print('-'*80)
                print('ERROR: {} was not found -- either update your ModDir setting in'.format(self.modlist_pathname))
                print('hfinject.ini or make sure that your modlist file is set up properly.')
                print('-'*80)
        else:
            print('-'*80)
            print('ERROR: hfinject.ini did not contain a ModDir attribute inside the')
            print('"main" section.  Make sure that hfinject.ini is populated!')
            print('-'*80)

    def _get_mod_path(self, filename):
        """
        Returns a valid path to the given `filename`, dealing with relative dir
        names if need be.
        """
        if os.path.isabs(filename):
            return filename
        else:
            return os.path.join(self.mod_dir, filename)

    def _get_modfiles(self, filename):
        """
        Reads a list of modfiles to load from the given `filename`.  Will
        recurse through `!include` statements, if found.  Will also update
        our mtime cache for this file
        """

        self.mtimes[filename] = os.path.getmtime(filename)

        to_load = []
        with open(filename) as df:
            for line in df:
                line = line.strip()
                if line == '':
                    continue
                if line[0] == '#':
                    continue

                if line.lower().startswith('!include'):
                    split_include = line.split(maxsplit=1)
                    if len(split_include) == 2:
                        included_filename = self._get_mod_path(split_include[1])
                        if os.path.exists(included_filename):
                            print('{} includes file {}'.format(filename, included_filename))
                            to_load.extend(self._get_modfiles(included_filename))
                            self.file_includes.add(included_filename)
                        else:
                            print('WARNING: Included file {} not found'.format(included_filename))
                    else:
                        print('WARNING: Invalid !include found: {}'.format(line))
                else:
                    # We got a modfile line, so add it to our list
                    mod_path = self._get_mod_path(line)
                    if os.path.exists(mod_path):
                        to_load.append(mod_path)
                    else:
                        print('WARNING: {} not found'.format(mod_path))

        return to_load

    def load_modlist(self):
        """
        Loads our modlist, if needed
        """

        # Get a list of files to check.  Ordinarily this'll just be the single main
        # modfile, but if we've processed any `!include` statements, we might have
        # more than one.  If *any* file mtime isn't present in our `self.mtimes`, or
        # if its mtime doesn't match, we'll re-load the whole lot.
        files_to_check = [self.modlist_pathname]
        files_to_check.extend(list(self.file_includes))

        # Now do that mtime check.
        do_load = False
        for file_to_check in files_to_check:
            cur_mtime = os.path.getmtime(file_to_check)
            if file_to_check in self.mtimes:
                if self.mtimes[file_to_check] != cur_mtime:
                    print('{} has been updated, loading modlist...'.format(file_to_check))
                    do_load = True
                    break
            else:
                print('{} has never been read, loading modlist...'.format(file_to_check))
                do_load = True
                break
        if not do_load:
            print('No changes to modlist, skipping modlist parsing.')
            return

        # Clear out our `!include` cache, since we're re-reading from the start.
        self.file_includes = set()

        # ... and get going.
        self.to_load = self._get_modfiles(self.modlist_pathname)
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
        if pathname.endswith('.gz'):
            df = gzip.open(pathname, mode='rt')
        else:
            df = open(pathname)
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
        df.close()

        self.mod_data[pathname] = statements
        return statements

    def response(self, flow):

        # Don't do anything if we're not initialized
        if not self.initialized:
            print('-'*80)
            print('modlist.txt was not found; check your hfinject.ini file and re-load')
            print('-'*80)
            return

        # If we *are* initialized, continue with our processing
        if flow.request.path.startswith('/v2/client/') and flow.request.path.endswith('/pc/oak/verification'):

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
