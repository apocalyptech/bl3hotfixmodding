#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright 2019-2022 Christopher J. Kucera
# <cj@apocalyptech.com>
# <http://apocalyptech.com/contact.php>
#
# Borderlands 3 / Wonderlands Hotfix Injector is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Borderlands 3 / Wonderlands Hotfix Injector is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Borderlands 3 / Wonderlands Hotfix Injector.  If not, see
# <https://www.gnu.org/licenses/>.

import os
import re
import sys
import gzip
import json
import string
import configparser

class GameInjector:
    """
    Generic class to describe how to inject hotfixes for a generic game.  Requires that
    a few attributes be filled in for implementing classes, namely `shortname`,
    `codename`, and `default_micropatch_name.  This was originally abstracted out because
    we needed to handle type-11 hotfixing pretty differently between BL3 and Wonderlands,
    but in August 2022 I figured out some alternat objects to use which work identically
    between both games.  As it stands right now, it's a bit stupid to even bother
    subclassing these things -- should maybe just pass those three required attributes
    into the constructor or something.  But whatever, will leave it for now.
    """

    # Game identifiers
    shortname = None
    codename = None

    # Default micropatch service name
    default_micropatch_name = None

    # Type-11 Hotfix parameters.  We need an object+attr to inject into, and a default mesh
    # to restore it to at the end.
    type_11_obj = '/Game/Pickups/Ammo/BPAmmoItem_Pistol.Default__BPAmmoItem_Pistol_C'
    type_11_attr = 'ItemMeshComponent.Object..StaticMesh'
    type_11_default = '/Game/Pickups/Ammo/Model/Meshes/SM_ammo_pistol.SM_ammo_pistol'

    # Meshes to use for type-11 delays
    type_11_delay_meshes = [
            '/Engine/EditorMeshes/Camera/SM_CraneRig_Arm.SM_CraneRig_Arm',
            '/Engine/EditorMeshes/Camera/SM_CraneRig_Base.SM_CraneRig_Base',
            '/Engine/EditorMeshes/Camera/SM_CraneRig_Body.SM_CraneRig_Body',
            '/Engine/EditorMeshes/Camera/SM_CraneRig_Mount.SM_CraneRig_Mount',
            '/Engine/EditorMeshes/Camera/SM_RailRig_Mount.SM_RailRig_Mount',
            '/Engine/EditorMeshes/Camera/SM_RailRig_Track.SM_RailRig_Track',
            ]

    # How many delay statements per map should we inject?
    type_11_delay_count = 2

    # Regex to detect type-11 hotfixes.  We can use string .startswith() and
    # some splitting/slicing to run this ~40% faster, but it honestly doesn't
    # seem worth it; it's still down in the hundredths of seconds for my
    # entire mod set.
    type_11_re = re.compile(r'^SparkEarlyLevelPatchEntry,\(1,11,[01],(?P<map_name>[A-Za-z0-9_]+)\),.*')

    def __init__(self, config):

        # Vars given to the initializers
        self.upper = self.shortname.upper()
        self.verification_end = f'/pc/{self.codename}/verification'
        moddir_param = f'moddir_{self.shortname}'

        # Various bits of data
        self.mtimes = {}
        self.file_includes = set()
        self.mod_data = {}
        self.to_load = []
        self.next_prefix = 0
        self.mod_dir = None
        self.modlist_pathname = None
        self.initialized = False

        if 'main' in config and moddir_param in config['main']:
            self.mod_dir = config['main'][moddir_param]
            self.modlist_pathname = os.path.join(self.mod_dir, 'modlist.txt')
            if os.path.exists(self.modlist_pathname):
                self.initialized = True
                self.output('-'*80)
                self.output(f'Initialized with mod directory: {self.mod_dir}')
                self.output(f'Path to modlist.txt: {self.modlist_pathname}')
                self.output('-'*80)
            else:
                self.output('-'*80)
                self.output(f'ERROR: {self.modlist_pathname} was not found -- either update your moddir setting in')
                self.output('hfinject.ini or make sure that your modlist file is set up properly.')
                self.output('-'*80)
        else:
            self.output('-'*80)
            self.output(f'ERROR: hfinject.ini did not contain a {moddir_param} attribute inside the')
            self.output('"main" section.  Make sure that hfinject.ini is populated!')
            self.output('-'*80)

    def output(self, line):
        print(f'{self.upper} | {line}')

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
                            self.output(f'{filename} includes file {included_filename}')
                            to_load.extend(self._get_modfiles(included_filename))
                            self.file_includes.add(included_filename)
                        else:
                            self.output(f'WARNING: Included file {included_filename} not found')
                    else:
                        self.output(f'WARNING: Invalid !include found: {line}')
                else:
                    # We got a modfile line, so add it to our list
                    mod_path = self._get_mod_path(line)
                    if os.path.exists(mod_path):
                        to_load.append(mod_path)
                    else:
                        self.output(f'WARNING: {mod_path} not found')

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
                    self.output(f'{file_to_check} has been updated, loading modlist...')
                    do_load = True
                    break
            else:
                self.output(f'{file_to_check} has never been read, loading modlist...')
                do_load = True
                break
        if not do_load:
            self.output('No changes to modlist, skipping modlist parsing.')
            return

        # Clear out our `!include` cache, since we're re-reading from the start.
        self.file_includes = set()

        # ... and get going.
        self.to_load = self._get_modfiles(self.modlist_pathname)
        self.output('Set {} mod(s) to load'.format(len(self.to_load)))

    def process_mod(self, pathname):

        # Make sure the mod file exists, and fail gracefully rather than allowing
        # an exception
        if not os.path.exists(pathname):
            if pathname in self.mtimes:
                del self.mtimes[pathname]
            self.output(f'WARNING: {pathname} not found')
            return ([], [], set())

        # Now continue on
        hf_counter = 0
        cur_mtime = os.path.getmtime(pathname)
        if pathname in self.mtimes and self.mtimes[pathname] == cur_mtime:
            return self.mod_data[pathname]
        self.output(f'Processing {pathname}')
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
            if line[0] == '@':
                # ignore BLIMP tags
                continue

            # Turn this into "official" hotfix JSON
            try:
                (hftype, hf) = line.split(',', 1)
            except ValueError as e:
                self.output(f'ERROR: Line could not be processed as hotfix, aborting this mod: {line}')
                return []
            hotfix_struct = {
                    'key': '{}-Apoc{}-{}'.format(hftype, prefix, hf_counter),
                    'value': hf,
                    }
            hf_counter += 1

            # Check to see if this is a Type-11 hotfix
            match = self.type_11_re.match(line)
            if match:
                # Found a type-11; process it specially
                type_11s.append(hotfix_struct)
                type_11_maps.add(match.group('map_name'))
            else:
                # Regular hotfix
                statements.append(hotfix_struct)

        df.close()

        self.mod_data[pathname] = (statements, type_11s, type_11_maps)
        return self.mod_data[pathname]

    def can_handle_response(self, request_path):
        return request_path.startswith('/v2/client/') and request_path.endswith(self.verification_end)

    def handle_response(self, flow):

        # Don't do anything if we're not initialized
        if not self.initialized:
            self.output('-'*80)
            self.output('modlist.txt was not found; check your hfinject.ini file and re-load')
            self.output('-'*80)
            return

        # Get the raw data
        gzipped = False
        if 'Content-Encoding' in flow.response.headers and flow.response.headers['Content-Encoding'] == 'gzip':
            raw_data = gzip.decompress(flow.response.data.content)
            gzipped = True
        else:
            raw_data = flow.response.data.content

        # Parse the existing services data
        have_json = False
        try:
            cur_data = json.loads(raw_data.decode('utf8'))
            if type(cur_data) == dict and 'services' in cur_data:
                have_json = True
        except json.decoder.JSONDecodeError as e:
            pass

        # If we didn't get JSON, or the JSON isn't formatted how we expect, just pass through the data.
        if not have_json:
            if gzipped:
                flow.response.data.content = gzip.compress(raw_data)
            else:
                flow.response.data.content = raw_data
            return

        # Find our Micropatch service, or create a new one
        micropath_service = None
        for service in cur_data['services']:
            if service['service_name'] == 'Micropatch':
                micropatch_service = service
                break
        if not micropatch_service:
            micropatch_service = {
                    'service_name': 'Micropatch',
                    'configuration_group': self.default_micropatch_name,
                    'configuration_version': '42',
                    'parameters': [],
                    }
            cur_data['services'].append(micropatch_service)

        # Load our mod list
        self.load_modlist()
        regulars = []
        type_11_maps = set()

        # Load each mod (or read from cache)
        type_11_count = 0
        for pathname in self.to_load:
            new_regulars, new_type_11s, new_type_11_maps = self.process_mod(pathname)
            regulars.extend(new_regulars)
            micropatch_service['parameters'].extend(new_type_11s)
            type_11_count += len(new_type_11s)
            type_11_maps |= new_type_11_maps

        # If we have any type-11 hotfixes, introduce some artificial delay statements.
        # We're keeping track of used lowercase names just in case we see mixed case
        if type_11_count > 0:
            seen_levels = set()
            delay_idx = 0
            for map_name in type_11_maps:
                map_name_lower = map_name.lower()
                if map_name_lower in seen_levels:
                    continue
                used_delays = 0
                for letter_mesh in self.type_11_delay_meshes:
                    micropatch_service['parameters'].append({
                        'key': f'SparkEarlyLevelPatchEntry-Delay-{delay_idx}',
                        'value': f'(1,1,0,{map_name}),{self.type_11_obj},{self.type_11_attr},0,,StaticMesh\'"{letter_mesh}"\'',
                        })
                    delay_idx += 1
                    used_delays += 1
                    if used_delays >= self.type_11_delay_count:
                        break
                micropatch_service['parameters'].append({
                    'key': f'SparkEarlyLevelPatchEntry-Delay-{delay_idx}',
                    'value': f'(1,1,0,{map_name}),{self.type_11_obj},{self.type_11_attr},0,,StaticMesh\'"{self.type_11_default}"\'',
                    })
                delay_idx += 1

        # Now concat everything and do the injection
        micropatch_service['parameters'].extend(regulars)
        injected = json.dumps(cur_data,
                ensure_ascii=False,
                separators=(',', ':'),
                )
        if gzipped:
            flow.response.data.content = gzip.compress(injected.encode('utf8'))
        else:
            flow.response.data.content = injected.encode('utf8')
        #if 'Content-Length' in flow.response.headers:
        #    # This isn't actually the case for GBX
        #    flow.response.headers['Content-Length'] = str(len(flow.response.data.content))

class BL3(GameInjector):

    # Game identifiers
    shortname = 'bl3'
    codename = 'oak'

    # Default micropatch service name
    default_micropatch_name = 'Oak_Crossplay_Default'

class WL(GameInjector):

    # Game identifiers
    shortname = 'wl'
    codename = 'daffodil'

    # Default micropatch service name
    default_micropatch_name = 'DaffodilLaneA'

class InjectHotfix:

    def __init__(self):

        # This happens if you're running mitmproxy via docker -- do a chdir to get to
        # where we're supposed to be, in that case.
        if os.getcwd() == '/':
            os.chdir(os.path.dirname(os.path.realpath(__file__)))

        # Create a default `hfinject.ini` if it doesn't already exist
        if not os.path.exists('hfinject.ini'):
            config = configparser.ConfigParser()
            config['main'] = {
                    'moddir_bl3': 'injectdata_bl3',
                    'moddir_wl': 'injectdata_wl',
                    }
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
        self.handlers = [
                BL3(config),
                WL(config),
                ]

    def response(self, flow):

        for handler in self.handlers:
            if handler.can_handle_response(flow.request.path):
                handler.handle_response(flow)
                break

addons = [
    InjectHotfix()
    ]
