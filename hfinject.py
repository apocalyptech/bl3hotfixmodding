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
import re
import sys
import gzip
import string
import configparser

class InjectHotfix:

    # Regex to detect type-11 hotfixes
    type_11_re = re.compile(r'^SparkEarlyLevelPatchEntry,\(1,11,[01],(?P<map_name>[A-Za-z0-9_]+)\),.*')

    # How many delay statements per map should we inject?
    type_11_delay_count = 2

    # Used letters, per-map, from the "SM_Letter" mesh set, so we know which ones
    # we have available to inject.
    used_sm_letters_by_map = {
            'atlashq_p': {'A', 'B', 'F', 'I', 'K', 'L', 'N', 'O', 'Q', 'S'},
            'bar_p': {'A', 'C', 'D', 'E', 'G', 'H', 'L', 'N', 'O', 'R', 'S', 'U', 'V'},
            'cityvault_p': {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'Y'},
            'covslaughter_p': {'C', 'O', 'V'},
            'creatureslaughter_p': {'C', 'O', 'V'},
            'desert_p': {'A', 'B', 'C', 'D', 'E', 'G', 'I', 'L', 'M', 'N', 'O', 'P', 'S', 'T', 'W'},
            'finalboss_p': {'B', 'M', 'N', 'O', 'T', 'W'},
            'mansion_p': {'A', 'E', 'M', 'T'},
            'marshfields_p': {'A', 'C', 'E', 'K', 'L', 'T'},
            'motorcade_p': {'B', 'C', 'E', 'I', 'J', 'K', 'L', 'N', 'R', 'W'},
            'motorcadefestival_p': {'A', 'B', 'C', 'D', 'E', 'G', 'I', 'K', 'L', 'N', 'O', 'S', 'T'},
            'motorcadeinterior_p': {'C', 'E', 'L', 'M', 'O', 'W'},
            'prologue_p': {'A', 'C', 'E', 'G', 'I', 'K', 'L', 'O', 'P', 'R', 'S', 'T', 'Y'},
            'sanctuary3_p': {'A', 'C', 'E', 'I', 'L', 'M', 'N', 'O', 'P', 'R', 'T', 'X', 'Z'},
            'strip_p': {'J', 'K', 'M', 'O', 'P', 'R', 'S', 'T', 'W'},
            'towers_p': {'A', 'C', 'D', 'E', 'F', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y'},
            'trashtown_p': {'A', 'H', 'I', 'L', 'N', 'R', 'S', 'T'},
            'wetlands_p': {'A', 'E', 'G', 'L', 'M', 'O', 'S', 'T'},
            'woods_p': {'H', 'M', 'S', 'U'},
            }

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
        type_11s = []
        type_11_maps = set()

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

            # Turn this into "official" hotfix JSON
            try:
                (hftype, hf) = line.split(',', 1)
            except ValueError as e:
                print('ERROR: Line could not be processed as hotfix, aborting this mod: {}'.format(line))
                return []
            hotfix_json ='{{"key":"{}-Apoc{}-{}","value":"{}"}}'.format(
                    hftype,
                    prefix,
                    hf_counter,
                    hf.replace('"', '\\"'),
                    )
            hf_counter += 1

            # Check to see if this is a Type-11 hotfix
            match = self.type_11_re.match(line)
            if match:
                # Found a type-11; process it specially
                type_11s.append(hotfix_json)
                type_11_maps.add(match.group('map_name'))
            else:
                # Regular hotfix
                statements.append(hotfix_json)

        df.close()

        self.mod_data[pathname] = (statements, type_11s, type_11_maps)
        return self.mod_data[pathname]

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

                # Load our mod list
                self.load_modlist()
                statements = []
                regulars = []
                type_11_maps = set()

                # Load each mod (or read from cache)
                for pathname in self.to_load:
                    new_regulars, new_type_11s, new_type_11_maps = self.process_mod(pathname)
                    regulars.extend(new_regulars)
                    statements.extend(new_type_11s)
                    type_11_maps |= new_type_11_maps

                # If we have any statements at this point, they're all type 11, so
                # introduce some artificial delay statements.  We're keeping track
                # of used lowercase names just in case we see mixed case
                if statements:
                    seen_levels = set()
                    delay_idx = 0
                    for map_name in type_11_maps:
                        map_name_lower = map_name.lower()
                        if map_name_lower in seen_levels:
                            continue
                        used_letters = 0
                        for letter in string.ascii_uppercase:
                            if map_name_lower in self.used_sm_letters_by_map and letter in self.used_sm_letters_by_map[map_name_lower]:
                                continue
                            statements.append(f'{{"key":"SparkEarlyLevelPatchEntry-Delay-{delay_idx}","value":"(1,1,0,{map_name}),/Game/Gear/Game/Resonator/_Design/BP_Eridian_Resonator.Default__BP_Eridian_Resonator_C,StaticMeshComponent.Object..StaticMesh,0,,StaticMesh\'\\"/Game/LevelArt/Environments/_Global/Letters/Meshes/SM_Letter_{letter}.SM_Letter_{letter}\\"\'"}}')
                            delay_idx += 1
                            used_letters += 1
                            if used_letters >= self.type_11_delay_count:
                                break
                        statements.append(f'{{"key":"SparkEarlyLevelPatchEntry-Delay-{delay_idx}","value":"(1,1,0,{map_name}),/Game/Gear/Game/Resonator/_Design/BP_Eridian_Resonator.Default__BP_Eridian_Resonator_C,StaticMeshComponent.Object..StaticMesh,0,,StaticMesh\'\\"/Game/Gear/Game/Resonator/Model/Meshes/SM_Eridian_Resonator.SM_Eridian_Resonator\\"\'"}}')
                        delay_idx += 1

                # Now concat everything and do the injection
                statements.extend(regulars)
                if statements:
                    to_inject = ',' + ','.join(statements)
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
