#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import re
import sys
import csv
import platform
import itertools
from bl3data.bl3data import BL3Data
from bl3hotfixmod.bl3hotfixmod import Balance

if 'cpython' in platform.python_implementation().lower():
    print("")
    print("This app is slow and inefficient.  PyPy3 won't help with the")
    print("inefficiency, but it *will* improve runtimes considerably, by")
    print("something like 6x.  It's recommended to quit now and re-launch")
    print("with PyPy3.")
    print("")
    print("Hit Enter to continue anyway, but don't expect anything fast.")
    print("")
    sys.stdout.write("Ctrl-C to exit, Enter to continue> ")
    sys.stdout.flush()
    sys.stdin.readline()

data = BL3Data()

part_cache = {}

class PartTreeNode(object):
    """
    A node in a Part tree.  Using some legacy terminology here; "apls" used to refer
    to the PartSet ActorPartLists structure, but we're using our Balance objects
    instead.
    """

    def __init__(self, data, parent, part_set, apls, level=0):
        self.data = data
        self.parent = parent
        self.part_set = part_set
        self.apls = apls
        self.level = level
        self.children = []
        self.leaf_count = 0

        # Debug, pff.
        #print('{}{}'.format('  '*level, part_set))

        found_parts = False
        while not found_parts:
            if len(self.apls) == 0:
                break
            self.apl = self.apls[0]
            if len(self.apl.partlist) == 0:
                self.apls = self.apls[1:]
            else:
                found_parts = True

        if not found_parts:
            self.leaf_count = 1 
            return

        # Loop through parts to find out which ones actually apply here.
        parts = []
        for part in self.apl.partlist:
            part_name = part.part_name
            if part_name == 'None':
                parts.append(None)
            else:
                (excluders, dependencies) = self._get_constraints(part_name)

                # Process exclusions
                if len(excluders) > 0:
                    excluded = False
                    for excl in excluders:
                        if self._has_part(excl):
                            #print('Excluded {} because of {}'.format(part_name, excl))
                            excluded = True
                            break
                    if excluded:
                        continue

                # Process dependencies
                if len(dependencies) > 0:
                    has_dep = False
                    for dep in dependencies:
                        if self._has_part(dep):
                            has_dep = True
                            break
                    if not has_dep:
                        #print('Dependency fail for {}: {} ({})'.format(part_name, dependencies, self.part_set))
                        continue

                # If we got here, it's a valid part.
                parts.append(part_name)

        # Okay, now we've got a sanitized part list, put together a list of children
        possibilities = []
        if self.apl.select_multiple:
            # We're assuming that anything with weighted parts does NOT have
            # zero-weight parts.  TODO: maybe check that, later?
            for mult in range(self.apl.num_min, self.apl.num_max+1):
                if mult == 0:
                    possibilities.append(set())
                else:
                    possibilities.extend([set(c) for c in itertools.combinations(parts, mult)])
        else:
            possibilities.extend([set([p]) for p in parts])

        # Now loop through the possibilities. Note that in some cases we might not have
        # any parts which can be valid here, so be sure to recurse down with an empty
        # set.
        if len(possibilities) > 0:
            for possibility in possibilities:
                self.children.append(PartTreeNode(self.data, self, possibility, self.apls[1:], self.level+1))
        else:
            self.children.append(PartTreeNode(self.data, self, set(), self.apls[1:], self.level+1))

        # Update our leaf count as we go.
        self.leaf_count += sum([child.leaf_count for child in self.children])

        # Memory efficiency!  Hah.  Right.  Anyway, we never recurse back into
        # these things once they're created, so why not just get rid of 'em?
        # Honestly we probably shouldn't even bother setting up a children array
        # in the first place.  I'll leave it in anyway; if we comment this, we'd
        # be able to poke through the tree if we wanted, for some reason.
        self.children = None

    def _get_constraints(self, part_name):

        # Breaking OOO here, ah well.
        global part_cache

        if part_name not in part_cache:

            excluders = set()
            dependencies = set()

            if part_name == '/Game/Gear/GrenadeMods/_Design/PartSets/Part_Manufacturer/GM_Part_Manufacturer_06_Pangolin':
                # We can't serialize this object for some reason.  The uasset files do not include
                # the strings Excluders or Dependencies, though, so we should be good to leave them
                # blank here.
                pass
            else:
                part_data = self.data.get_data(part_name)
                found_export = False
                for export in part_data:
                    if export['export_type'].startswith('BPInvPart_'):
                        found_export = True
                        if 'Excluders' in export:
                            for excluder in export['Excluders']:
                                if 'export' in excluder:
                                    # WTF is going on here?  So far, this object seems to just reference *itself* in here?
                                    # /Game/Gear/Shields/_Design/PartSets/Part_Augment/Safespace/Part_Shield_Aug_Knockback
                                    # Just gonna print a warning...
                                    print('WARNING: {} Excluders references itself?'.format(part_name))
                                else:
                                    excluders.add(excluder[1])
                        if 'Dependencies' in export:
                            for dependency in export['Dependencies']:
                                dependencies.add(dependency[1])
                        break

                if not found_export:
                    raise Exception('Could not find export for {}'.format(part_name))

            part_cache[part_name] = (excluders, dependencies)

        return part_cache[part_name]

    def _has_part(self, part_name):
        if part_name in self.part_set:
            return True
        if self.parent is not None:
            return self.parent._has_part(part_name)
        return False

    def count_leaves(self):
        """
        Manually count leaves; shouldn't be necessary to do this since we
        update as we go.
        """
        if len(self.children) == 0:
            return 1
        else:
            return sum([child.count_leaves() for child in self.children])

class BalanceTree(object):
    """
    A wrapper around the "stock" Balance object to do our recursive tree nonsense.
    """

    def __init__(self, bal_name, data):
        self.bal_name = bal_name
        self.data = data

        # Load ourselves
        self.bal = Balance.from_data(data, bal_name)

        # Start processing our part tree
        self.tree = PartTreeNode(self.data, None, set(), self.bal.categories)

    def gun_count(self, anointment_additions=None):
        """
        Counts the leaves of our tree
        """
        if anointment_additions \
                and 'RuntimeGenericPartList' in self.bal.raw_bal_data \
                and 'bEnabled' in self.bal.raw_bal_data['RuntimeGenericPartList'] \
                and self.bal.raw_bal_data['RuntimeGenericPartList']['bEnabled'] \
                and len(self.bal.raw_bal_data['RuntimeGenericPartList']['PartList']) > 0:
            if self.bal_name in anointment_additions:
                addition = anointment_additions[self.bal_name]
            else:
                addition = 0
            return self.tree.leaf_count * (len(self.bal.raw_bal_data['RuntimeGenericPartList']['PartList']) + addition)
        else:
            return self.tree.leaf_count

# Balances to loop through
gun_balances = []

# Some text massaging
transforms = {
        'sniperrifles': 'Sniper Rifles',
        'sniperifles': 'Sniper Rifles',
        'assaultrifles': 'ARs',
        'assaultrifle': 'ARs',
        'shotgun': 'Shotguns',
        'pistol': 'Pistols',
        'heavyweapons': 'Heavy Weapons',
        'hw': 'Heavy Weapons',

        '_etech': 'E-Tech',

        'childrenofthevault': 'COV',
        'ted': 'Tediore',
        'vla': 'Vladof',
        'tor': 'Torgue',
        'atl': 'Atlas',
        'mal': 'Maliwan',
        }

# "Regular" guns - second glob just matches on etech
for glob_pattern, re_pattern in [
        ('/Game/Gear/Weapons/*/*/_Shared/_Design/*Balance*/Balance_*',
            r'^/Game/Gear/Weapons/(?P<guntype>.*?)/(?P<manufacturer>.*?)/.*',
            ),
        ('/Game/Gear/Weapons/_Shared/_Design/_Manufacturers/*/_Design/*/*/*Balance*/Balance_*',
            r'/Game/Gear/Weapons/_Shared/_Design/_Manufacturers/(?P<rarity_suffix>.*?)/_Design/(?P<guntype>.*?)/(?P<manufacturer>.*?)/.*',
            ),
        ]:
    pat = re.compile(re_pattern)
    for obj_name in data.glob(glob_pattern):

        # Skip some stuff that we probably don't want to consider
        if 'Fabricator' in obj_name or 'FirstGun' in obj_name or 'No_Elemental' in obj_name:
            continue

        # Strip out some info from the object name
        suffix = None
        match = pat.match(obj_name).groupdict()
        if 'rarity_suffix' in match:
            rarity_suffix = match['rarity_suffix']

            lower = obj_name.lower()
            if 'veryrare' in lower:
                rarity = '04/Very Rare'
            elif 'rare' in lower:
                rarity = '03/Rare'
            else:
                raise Exception('Unknown rarity in {}'.format(obj_name))

            rarity = '{} {}'.format(rarity, transforms.get(rarity_suffix.lower(), default=rarity_suffix))
        else:
            lower = obj_name.lower()
            if 'uncommon' in lower:
                rarity = '02/Uncommon'
            elif 'common' in lower:
                rarity = '01/Common'
            elif 'veryrare' in lower:
                rarity = '04/Very Rare'
            elif 'rare' in lower:
                rarity = '03/Rare'
            else:
                raise Exception('Unknown rarity in {}'.format(obj_name))

        # Now add it to our list
        gun_balances.append((
            transforms.get(match['manufacturer'].lower(), default=match['manufacturer']),
            transforms.get(match['guntype'].lower(), default=match['guntype']),
            rarity,
            obj_name,
            ))

# Sort the list so far
gun_balances.sort()

# Uniques /  Legendaries
for (label, balance_name) in [
        ("9-Volt", '/Game/Gear/Weapons/SMGs/Dahl/_Shared/_Design/_Unique/NineVolt/Balance/Balance_SM_DAHL_NineVolt'),
        ("AAA", '/Game/Gear/Weapons/Pistols/Dahl/_Shared/_Design/_Unique/AAA/Balance/Balance_DAL_PS_AAA'),
        ("ASMD", '/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/ASMD/Balance/Balance_MAL_SR_ASMD'),
        ("Agonizer 1500", '/Game/Gear/Weapons/HeavyWeapons/ChildrenOfTheVault/_Shared/_Design/_Unique/Terror/Balance/Balance_HW_COV_Terror'),
        ("Alchemist", '/Game/Gear/Weapons/AssaultRifles/Torgue/_Shared/_Design/_Unique/Alchemist/Balance/Balance_AR_TOR_Alchemist'),
        ("Amazing Grace", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/AmazingGrace/Balance/Balance_PS_JAK_AmazingGrace'),
        ("Amber Management", '/Game/Gear/Weapons/AssaultRifles/Torgue/_Shared/_Design/_Unique/AmberManagement/Balance/Balance_AR_TOR_AmberManagement'),
        ("AutoAimè", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/AutoAime/Balance/Balance_SR_DAL_AutoAime'),
        ("Baby Maker ++", '/Game/Gear/Weapons/Pistols/Tediore/Shared/_Design/_Unique/BabyMaker/Balance/Balance_PS_Tediore_BabyMaker'),
        ("Bangarang", '/Game/Gear/Weapons/Pistols/Tediore/Shared/_Design/_Unique/_Bangarang/Balance/Balance_PS_TED_Bangerang'),
        ("Barrage", '/Game/Gear/Weapons/AssaultRifles/Dahl/_Shared/_Design/_Unique/Barrage/Balance/Balance_DAL_AR_Barrage'),
        ("Bearcat", '/Game/Gear/Weapons/AssaultRifles/Torgue/_Shared/_Design/_Unique/Bearcat/Balance/Balance_AR_TOR_Bearcat'),
        ("Bekah", '/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/Bekah/Balance/Balance_AR_JAK_Bekah'),
        ("Bitch", '/Game/Gear/Weapons/SMGs/Hyperion/_Shared/_Design/_Unique/Bitch/Balance/Balance_SM_HYP_Bitch'),
        ("Black Flame", '/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/Brew/Balance/Balance_SG_TOR_Brewha'),
        ("Bone Shredder", '/Game/Gear/Weapons/Pistols/Vladof/_Shared/_Design/_Unique/BoneShredder/Balance/Balance_PS_VLA_BoneShredder'),
        ("Boom Sickle / Sickle", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/Sickle/Balance/Balance_AR_VLA_Sickle'),
        ("Boomer", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Boomer/Balance/Balance_SM_DAL_Boomer'),
        ("Brad Luck", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Trash/Balance/Balance_AR_COV_Trash'),
        ("Brainstormer", '/Game/Gear/Weapons/Shotguns/Hyperion/_Shared/_Design/_Unique/Redistributor/Balance/Balance_SG_HYP_Redistributor'),
        ("Brashi's Dedication", '/Game/Gear/Weapons/SniperRifles/Dahl/_Shared/_Design/_Unique/BrashisDedication/Balance/Balance_SR_DAL_BrashisDedication'),
        ("Breath of the Dying", '/Game/Gear/Weapons/AssaultRifles/Dahl/_Shared/_Design/_Unique/BOTD/Balance/Balance_DAL_AR_BOTD'),
        ("Buttplug", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/Buttplug/Balance/Balance_PS_JAK_Buttplug'),
        ("Carrier", '/Game/Gear/Weapons/AssaultRifles/Atlas/_Shared/_Design/_Unique/Carrier/Balance/Balance_ATL_AR_Carrier'),
        ("Cheap Tips", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/CheapTips/Balance/Balance_SM_HYP_CheapTips'),
        ("Chomper", '/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/Balrog/Balance/Balance_SG_Torgue_Balrog'),
        ("Cloud Kill", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/CloudKill/Balance/Balance_SM_MAL_CloudKill'),
        ("Cold Shoulder", '/Game/Gear/Weapons/SniperRifles/Vladof/_Shared/_Design/_Unique/Prison/Balance/Balance_VLA_SR_Prison'),
        ("Conference Call", '/Game/Gear/Weapons/Shotguns/Hyperion/_Shared/_Design/_Unique/ConferenceCall/Balance/Balance_SG_HYP_ConferenceCall'),
        ("Crader's EM-P5", '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/CraderMP5/Balance/Balance_SM_DAHL_CraderMP5'),
        ("Craps", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Craps/Balance/Balance_PS_TOR_Craps'),
        ("Creamer", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Creamer/Balance/Balance_HW_TOR_Creamer'),
        ("Creeping Death", '/Game/Gear/Weapons/Shotguns/Tediore/_Shared/_Design/_Unique/Sludge/Balance/Balance_SG_TED_Sludge'),
        ("Crit", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Crit/Balance/Balance_SM_MAL_Crit'),
        ("Crossroad", '/Game/Gear/Weapons/SMGs/Hyperion/_Shared/_Design/_Unique/Crossroad/Balance/Balance_SM_HYP_Crossroad'),
        ("Cutsman", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Cutsman/Balance/Balance_SM_MAL_Cutsman'),
        ("Damned", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/Damn/Balance/Balance_AR_VLA_Damn'),
        ("Dead Chamber", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/Malevolent/Balance/Balance_PS_JAK_Malevolent'),
        ("Destructo Spinner", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/DestructoSpin/Balance/Balance_SM_MAL_DestructoSpin'),
        ("Devastator", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/Devestator/Balance/Balance_PS_TOR_Devestator'),
        ("Devils Foursum", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/Foursum/Balance/Balance_PS_TOR_4SUM'),
        ("Devoted", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Devoted/Balance/Balance_SM_MAL_Devoted'),
        ("Digby's Smooth Tube", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Digby/Balance/Balance_DAL_AR_Digby'),
        ("E-Gone", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Egon/Balance/Balance_SM_MAL_Egon'),
        ("Earworm", '/Game/Gear/Weapons/AssaultRifles/Dahl/_Shared/_Design/_Unique/Earworm/Balance/Balance_DAL_AR_Earworm'),
        ("Echo / Breeder", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/Echo/Balance/Balance_PS_TOR_Echo'),
        ("Ember's Purge", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/EmbersPurge/Balance/Balance_SM_MAL_EmbersPurge'),
        ("Extreme Hangin' Chadd", '/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/Chad/Balance/Balance_PS_COV_Chad'),
        ("Face-puncher", '/Game/Gear/Weapons/Shotguns/Hyperion/_Shared/_Design/_Unique/Brick/Balance/Balance_SG_HYP_Brick'),
        ("Faisor", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/Faisor/Balance/Balance_AR_VLA_Faisor'),
        ("Fearmonger", '/Game/PatchDLC/BloodyHarvest/Gear/Weapons/Shotguns/Hyperion/_Shared/_Design/_Unique/Fearmonger/Balance/Balance_SG_HYP_ETech_Fearmonger'),
        ("Fingerbiter", '/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/Fingerbiter/Balance/Balance_SG_JAK_Fingerbiter'),
        ("Flakker", '/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/Flakker/Balance/Balance_SG_Torgue_Flakker'),
        ("Freeman", '/Game/Gear/Weapons/HeavyWeapons/ATL/_Shared/_Design/_Unique/Freeman/Balance/Balance_HW_ATL_Freeman'),
        ("Gatling Gun", '/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/GatlingGun/Balance/Balance_AR_JAK_04_GatlingGun'),
        ("Gettleburger", '/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/BurgerCannon/Balance/Balance_HW_TOR_BurgerCannon'),
        ("Girth Blaster Elite", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/Nurf/Balance/Balance_PS_TOR_Nurf'),
        ("Good Juju", '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/Juju/Balance/Balance_DAL_AR_ETech_Juju'),
        ("Gunerang", '/Game/Gear/Weapons/Pistols/Tediore/Shared/_Design/_Unique/Gunerang/Balance/Balance_PS_TED_Gunerang'),
        ("Hail", '/Game/Gear/Weapons/AssaultRifles/Dahl/_Shared/_Design/_Unique/Hail/Balance/Balance_DAL_AR_Hail'),
        ("Hand of Glory", '/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/HandOfGlory/Balance/Balance_AR_JAK_HandOfGlory'),
        ("Handsome Jackhammer", '/Game/Gear/Weapons/SMGs/Hyperion/_Shared/_Design/_Unique/Handsome/Balance/Balance_SM_HYP_Handsome'),
        ("Headsplosion", '/Game/Gear/Weapons/SniperRifles/Jakobs/_Shared/_Design/_Unique/Headsplosion/Balance/Balance_SR_JAK_Headsplosion'),
        ("Heart Breaker", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/HeartBreaker/Balance/Balance_SG_HYP_HeartBreaker'),
        ("Heckle", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/HeckelAndHyde/Heckle/Balance/Balance_PS_TOR_Heckle'),
        ("Hellfire", '/Game/Gear/Weapons/SMGs/Dahl/_Shared/_Design/_Unique/HellFire/Balance/Balance_SM_DAHL_HellFire'),
        ("Hellshock", '/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/Hellshock/Balance/Balance_PS_MAL_Hellshock'),
        ("Hellwalker", '/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/_Legendary/Hellwalker/Balance/Balance_SG_JAK_Hellwalker'),
        ("Hive", '/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/Hive/Balance/Balance_HW_TOR_Hive'),
        ("Hornet", '/Game/Gear/Weapons/Pistols/Dahl/_Shared/_Design/_Unique/Hornet/Balance/Balance_DAL_PS_Hornet'),
        ("Hot Drop", '/Game/Gear/Weapons/HeavyWeapons/ChildrenOfTheVault/_Shared/_Design/_Unique/HotDrop/Balance/Balance_HW_COV_HotDrop'),
        ("Hyde", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/HeckelAndHyde/Hyde/Balance/Balance_PS_TOR_Hyde'),
        ("Hyper-Hydrator", '/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/HyperHydrator/Balance/Balance_PS_MAL_HyperHydrator'),
        ("ION CANNON", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/IonCannon/Balance/Balance_HW_VLA_IonCannon'),
        ("ION LASER", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/IonLaser/Balance/Balance_SM_MAL_IonLaser'),
        ("Infinity", '/Game/Gear/Weapons/Pistols/Vladof/_Shared/_Design/_Unique/Infiniti/Balance/Balance_PS_VLA_Infiniti'),
        ("Jericho", '/Game/Gear/Weapons/HeavyWeapons/Vladof/_Shared/_Design/_Unique/CloudBurst/Balance/Balance_HW_VLA_CloudBurst'),
        ("Juliet's Dazzle", '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/Juliet/Balance/Balance_AR_TOR_Juliet_WorldDrop'),
        ("Just Kaus", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/JustCaustic/Balance/Balance_SM_HYP_JustCaustic'),
        ("Kaos", '/Game/Gear/Weapons/AssaultRifles/Dahl/_Shared/_Design/_Unique/Kaos/Balance/Balance_DAL_AR_Kaos'),
        ("Kenulox", '/Game/Gear/Weapons/SniperRifles/Dahl/_Shared/_Design/_Unique/WorldDestroyer/Balance/Balance_SR_DAL_WorldDestroyer'),
        ("Kevin's Chilly", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Kevins/Balance/Balance_SM_MAL_Kevins'),
        ("Kill-o'-the-Wisp", '/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Wisp/Balance/Balance_SG_MAL_Wisp'),
        ("King's Call / Queen's Call", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/GodMother/Balance/Balance_PS_JAK_GodMother'),
        ("Krakatoa", '/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/Krakatoa/Balance/Balance_MAL_SR_Krakatoa'),
        ("Kyb's Worth", '/Game/PatchDLC/Raid1/Gear/Weapons/KybsWorth/Balance/Balance_SM_MAL_KybsWorth'),
        ("L0V3M4CH1N3", '/Game/Gear/Weapons/SMGs/Hyperion/_Shared/_Design/_Unique/L0V3M4CH1N3/Balance/Balance_SM_HYP_L0V3M4CH1N3'),
        ("La Varlope", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Varlope/Balance/Balance_AR_TOR_Varlope'),
        ("Laser-Sploder", '/Game/Gear/Weapons/AssaultRifles/Torgue/_Shared/_Design/_Unique/LaserSploder/Balance/Balance_AR_TOR_LaserSploder'),
        ("Lead Sprinkler", '/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/LeadSprinkler/Balance/Balance_AR_JAK_LeadSprinkler'),
        ("Linc", '/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/_Unique/Drill/Balance/Balance_PS_ATL_Drill'),
        ("Linoge", '/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/Legion/Balance/Balance_PS_COV_Legion'),
        ("Long Musket", '/Game/Gear/Weapons/SMGs/Tediore/_Shared/_Design/_Unique/NotAFlamethrower/Balance/Balance_SM_TED_NotAFlamethrower'),
        ("Lucian's Call", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/LuciansCall/Balance/Balance_AR_VLA_LuciansCall'),
        ("Lucky 7", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Lucky7/Balance/Balance_PS_JAK_Lucky7'),
        ("Lyuda", '/Game/Gear/Weapons/SniperRifles/Vladof/_Shared/_Design/_Unique/Lyuda/Balance/Balance_VLA_SR_Lyuda'),
        ("Maggie", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/Maggie/Balance/Balance_PS_JAK_Maggie'),
        ("Magnificent", '/Game/Gear/Weapons/Pistols/Vladof/_Shared/_Design/_Unique/Magnificent/Balance/Balance_PS_VLA_Magnificent'),
        ("Malak's Bane", '/Game/Gear/Weapons/SniperRifles/Dahl/_Shared/_Design/_Unique/MalaksBane/Balance/Balance_SR_DAL_ETech_MalaksBane'),
        ("Manic Pixie Dream Gun", '/Game/Gear/Weapons/Shotguns/Tediore/_Shared/_Design/_Unique/FriendZone/Balance/Balance_SG_TED_FriendZone'),
        ("Masterwork Crossbow", '/Game/Gear/Weapons/SniperRifles/Hyperion/_Shared/_Design/_Unique/MasterworkCrossbow/Balance/Balance_SR_HYP_Masterwork'),
        ("Melt Facer", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/MeltFacer/Balance/Balance_SG_HYP_MeltFacer'),
        ("Mind-Killer", '/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/MouthPiece2/Balance/Balance_SG_MAL_Mouthpiece2'),
        ("Miss Moxxi's Vibra-Pulse", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/VibraPulse/Balance/Balance_SM_MAL_VibraPulse'),
        ("Mongol", '/Game/Gear/Weapons/HeavyWeapons/Vladof/_Shared/_Design/_Unique/Mongol/Balance/Balance_HW_VLA_Mongol'),
        ("Monocle", '/Game/Gear/Weapons/SniperRifles/Jakobs/_Shared/_Design/_Unique/Monocle/Balance/Balance_SR_JAK_Monocle'),
        ("Moonfire", '/Game/PatchDLC/Raid1/Gear/Weapons/HandCannon/Balance/Balance_PS_TOR_HandCannon'),
        ("Nemesis", '/Game/Gear/Weapons/Pistols/Dahl/_Shared/_Design/_Unique/Nemesis/Balance/Balance_DAL_PS_Nemesis'),
        ("Night Flyer", '/Game/Gear/Weapons/Pistols/Dahl/_Shared/_Design/_Unique/Rakkman/Balance/Balance_DAL_PS_Rakkman'),
        ("Night Hawkin", '/Game/Gear/Weapons/SMGs/Dahl/_Shared/_Design/_Unique/Demoskag/Balance/Balance_SM_DAL_Demoskag'),
        ("Nimble Jack", '/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/_Legendary/NimbleJack/Balance/Balance_SG_JAK_Nimble'),
        ("Nukem", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Nukem/Balance/Balance_HW_TOR_Nukem'),
        ("Null Pointer", '/Game/Gear/Weapons/_Shared/NPC_Weapons/Zero/ZeroForPlayer/Balance_SR_HYP_ZeroForPlayer'),
        ("Occultist", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/Troy/Balance/Balance_PS_TOR_Troy'),
        ("Ogre", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/Ogre/Balance/Balance_AR_VLA_Ogre'),
        ("Omniloader", '/Game/Gear/Weapons/Pistols/Dahl/_Shared/_Design/_Unique/Omniloader/Balance/Balance_DAL_PS_Omniloader'),
        ("One Pump Chump", '/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/_Legendary/OnePunch/Balance/Balance_SG_JAK_OnePunch'),
        ("P2P Networker", '/Game/PatchDLC/Raid1/Gear/Weapons/Link/Balance/Balance_SM_MAL_Link'),
        ("Pa's Rifle", '/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/PasRifle/Balance/Balance_AR_JAK_PasRifle'),
        ("Pain is Power / Embrace the Pain", '/Game/Gear/Weapons/AssaultRifles/ChildrenOfTheVault/_Shared/_Design/_Unique/KriegAR/Balance/Balance_AR_COV_KriegAR'),
        ("Peacemonger", '/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/_Unique/Warmonger/Balance/Balance_PS_ATL_Warmonger'),
        ("Pestilence", '/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/Contagion/Balance/Balance_PS_COV_Contagion'),
        ("Phebert", '/Game/Gear/Weapons/Shotguns/Hyperion/_Shared/_Design/_Unique/Phebert/Balance/Balance_SG_HYP_Phebert'),
        ("Polybius", '/Game/Gear/Weapons/Shotguns/Tediore/_Shared/_Design/_Unique/Polybius/Balance/Balance_SG_TED_Polybius'),
        ("Porta-Pooper 5000", '/Game/Gear/Weapons/HeavyWeapons/ChildrenOfTheVault/_Shared/_Design/_Unique/PortaPooper/Balance/Balance_HW_COV_PortaPooper'),
        ("Predatory Lending", '/Game/Gear/Weapons/SMGs/Hyperion/_Shared/_Design/_Unique/PredatoryLending/Balance/Balance_SM_HYP_PredatoryLending'),
        ("Projectile Recursion", '/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Recursion/Balance/Balance_SG_MAL_Recursion'),
        ("Psycho Stabber", '/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/PsychoStabber/Balance/Balance_PS_COV_PsychoStabber'),
        ("Quadomizer", '/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/Rampager/Balance/Balance_HW_TOR_Rampager'),
        ("R.Y.N.A.H.", '/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/RYNO/Balance/Balance_HW_TOR_RYNO'),
        ("Rebel Yell", '/Game/Gear/Weapons/AssaultRifles/Atlas/_Shared/_Design/_Unique/RebellYell/Balance/Balance_ATL_AR_RebelYell'),
        ("Redistributor", '/Game/Gear/Weapons/SMGs/Hyperion/_Shared/_Design/_Unique/Fork/Balance/Balance_SM_HYP_Fork'),
        ("Redistributor", '/Game/PatchDLC/Raid1/Gear/Weapons/Fork2/Balance/Balance_SM_HYP_Fork2'),
        ("Redline", '/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/RedLiner/Balance/Balance_SG_Torgue_RedLine'),
        ("Ripper", '/Game/Gear/Weapons/SMGs/Dahl/_Shared/_Design/_Unique/Ripper/Balance/Balance_SM_DAL_Ripper'),
        ("Robo-Melter", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/RoboMasher/Balance/Balance_PS_JAK_RoboMasher'),
        ("Rogue-Sight", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/SpyRevolver/Balance_PS_JAK_SpyRevolver'),
        ("Roisen's Thorns", '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/RoisensThorns/Balance/Balance_PS_TOR_RoisensThorns'),
        ("Rowan's Call", '/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/RowansCall/Balance/Balance_AR_JAK_RowansCall'),
        ("Ruby's Wrath", '/Game/Gear/Weapons/HeavyWeapons/ATL/_Shared/_Design/_Unique/RubysWrath/Balance/Balance_HW_ATL_RubysWrath'),
        ("S3RV-80S-EXECUTE", '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/Execute/Balance/Balance_PS_TED_Execute'),
        ("Sawbar", '/Game/Gear/Weapons/AssaultRifles/ChildrenOfTheVault/_Shared/_Design/_Unique/Sawbar/Balance/Balance_AR_COV_Sawbar'),
        ("Scorpio", '/Game/Gear/Weapons/Pistols/Tediore/Shared/_Design/_Unique/Sabre/Balance/Balance_PS_Tediore_Sabre'),
        ("Scourge", '/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/Swarm/Balance/Balance_HW_TOR_Swarm'),
        ("Scoville", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/Scoville/Balance/Balance_PS_TOR_Scoville'),
        ("Sellout", '/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/SuckerPunch/Balance/Balance_PS_MAL_SuckerPunch'),
        ("Shrieking Devil", '/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Shriek/Balance/Balance_SG_MAL_Shriek'),
        ("SkekSil", '/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/Skeksis/Balance/Balance_PS_COV_Skeksis'),
        ("Sledge's Shotgun / Sledge's Super Shotgun", '/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/_Legendary/Sledge/Balance/Balance_SG_JAK_LGD_Sledge'),
        ("Sleeping Giant", '/Game/Gear/Weapons/SMGs/Dahl/_Shared/_Design/_Unique/SleepingGiant/Balance/Balance_SM_DAL_SleepingGiant'),
        ("Slow Hand", '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/SlowHand/Balance/Balance_SG_HYP_SlowHand'),
        ("Smart-Gun", '/Game/Gear/Weapons/SMGs/Tediore/_Shared/_Design/_Unique/SpiderMind/Balance/Balance_SM_TED_SpiderMind'),
        ("Soleki Protocol", '/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/Soleki/Balance/Balance_MAL_SR_Soleki'),
        ("Stalker", '/Game/PatchDLC/BloodyHarvest/Gear/Weapons/SniperRifles/Dahl/_Design/_Unique/Frostbolt/Balance/Balance_SR_DAL_ETech_Frostbolt'),
        ("Star Helix", '/Game/Gear/Weapons/AssaultRifles/Dahl/_Shared/_Design/_Unique/StarHelix/Balance/Balance_DAL_AR_StarHelix'),
        ("Starkiller", '/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/Starkiller/Balance/Balance_PS_MAL_Starkiller'),
        ("Storm / Firestorm", '/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/Storm/Balance/Balance_MAL_SR_LGD_Storm'),
        ("Super Shredifier", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/Shredifier/Balance/Balance_AR_VLA_Sherdifier'),
        ("Superball", '/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/Plumber/Balance/Balance_PS_MAL_Plumber'),
        ("Superstreamer", '/Game/PatchDLC/EventVDay/Gear/Weapon/_Unique/TwitchPrime/Balance/Balance_SG_TED_Twitch'),
        ("T.K.'s Wave + variants", '/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/TheWave/Balance/Balance_SG_JAK_Unique_Wave'),
        ("THE TWO TIME", '/Game/Gear/Weapons/SniperRifles/Hyperion/_Shared/_Design/_Unique/TwoTime/Balance/Balance_SR_HYP_TwoTime'),
        ("Tankman's Shield", '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/Tankman/Balance/Balance_SR_HYP_Tankman'),
        ("Ten Gallon", '/Game/Gear/Weapons/SMGs/Tediore/_Shared/_Design/_Unique/TenGallon/Balance/Balance_SM_TED_TenGallon'),
        ("Terminal Polyaimorous", '/Game/PatchDLC/EventVDay/Gear/Weapon/_Unique/PolyAim/Balance/Balance_SM_MAL_PolyAim'),
        ("The Big Succ", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/BigSucc/Balance_AR_VLA_BigSucc'),
        ("The Boo", '/Game/Gear/Weapons/SMGs/Tediore/_Shared/_Design/_Unique/Beans/Balance/Balance_SM_TED_Beans'),
        ("The Boring Gun", '/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/TheBoringGun/Balance/Balance_SG_TOR_Boring'),
        ("The Butcher", '/Game/Gear/Weapons/Shotguns/Hyperion/_Shared/_Design/_Unique/TheButcher/Balance/Balance_SG_HYP_TheButcher'),
        ("The Companion", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/MelsCompanion/Balance/Balance_PS_JAK_MelsCompanion'),
        ("The Dictator", '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/Dictator/Balance/Balance_AR_VLA_Dictator'),
        ("The Duc", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/TheDuc/Balance/Balance_PS_JAK_TheDuc'),
        ("The Emperor's Condiment", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Emporer/Balance/Balance_SM_MAL_Emporer'),
        ("The Flood", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/Doc/Balance/Balance_PS_JAK_Doc'),
        ("The Garcia", '/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/_Legendary/Garcia/Balance/Balance_SG_JAK_Garcia'),
        ("The Horizon", '/Game/Gear/Weapons/Shotguns/Tediore/_Shared/_Design/_Unique/Horizon/Balance/Balance_SG_TED_Horizon'),
        ("The Hunt(ed)", '/Game/Gear/Weapons/SniperRifles/Jakobs/_Shared/_Design/_Unique/TheHunter/Hunted/Balance/Balance_SR_JAK_Hunted'),
        ("The Hunt(er)", '/Game/Gear/Weapons/SniperRifles/Jakobs/_Shared/_Design/_Unique/TheHunter/Balance/Balance_SR_JAK_Hunter'),
        ("The Hunt(ress)", '/Game/Gear/Weapons/SniperRifles/Jakobs/_Shared/_Design/_Unique/TheHunter/Huntress/Balance/Balance_SR_JAK_Huntress'),
        ("The Ice Queen", '/Game/Gear/Weapons/SniperRifles/Jakobs/_Shared/_Design/_Unique/IceQueen/Balance/Balance_SR_JAK_IceQueen'),
        ("The Killing Word", '/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/Mouthpiece/Balance/Balance_PS_COV_Mouthpiece'),
        ("The Leech", '/Game/Gear/Weapons/Pistols/Vladof/_Shared/_Design/_Unique/TheLeech/Balance/Balance_PS_VLA_TheLeech'),
        ("The Lob", '/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/TheLob/Balance/Balance_SG_Torgue_ETech_TheLob'),
        ("Thumper", '/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/Thumper/Balance/Balance_SG_Torgue_Thumper'),
        ("Thunderball Fists", '/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/ThunderballFist/Balance/Balance_PS_MAL_ThunderballFists'),
        ("Tiggs' Boom", '/Game/PatchDLC/Raid1/Gear/Weapons/TiggsBoom/Balance/Balance_SG_Torgue_TiggsBoom'),
        ("Traitor's Death", '/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/TraitorsDeath/Balance/Balance_AR_JAK_TraitorsDeath'),
        ("Trevonator", '/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Trev/Balance/Balance_SG_MAL_Trev'),
        ("Try-Bolt", '/Game/Gear/Weapons/AssaultRifles/Torgue/_Shared/_Design/_Unique/TryBolt/Balance/Balance_AR_TOR_TryBolt'),
        ("Tsunami", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Tsunami/Balance/Balance_SM_MAL_Tsunami'),
        ("Tunguska", '/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/Tunguska/Balance/Balance_HW_TOR_Tunguska'),
        ("Unforgiven", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/Unforgiven/Balance/Balance_PS_JAK_Unforgiven'),
        ("Vanquisher", '/Game/Gear/Weapons/SMGs/Dahl/_Shared/_Design/_Unique/Vanquisher/Balance/Balance_SM_DAHL_Vanquisher'),
        ("Vault Hero", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/E3/Balance_SM_MAL_E3'),
        ("Vosk's Deathgrip", '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/DeathGrip/Balance/Balance_SG_MAL_DeathGrip'),
        ("Wagon Wheel", '/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/WagonWheel/Balance/Balance_PS_JAK_WagonWheel'),
        ("Warlord", '/Game/Gear/Weapons/AssaultRifles/Dahl/_Shared/_Design/_Unique/Warlord/Balance/Balance_DAL_AR_Warlord'),
        ("Wedding Invitation", '/Game/PatchDLC/EventVDay/Gear/Weapon/_Unique/WeddingInvitation/Balance/Balance_SR_JAK_WeddingInvite'),
        ("Westergun", '/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/westergun/Balance/Balance_SM_MAL_westergun'),
        ("Woodblocker", '/Game/Gear/Weapons/SniperRifles/Hyperion/_Shared/_Design/_Unique/Woodblocks/Balance/Balance_SR_HYP_Woodblocks'),
        ("XZ41", '/Game/Gear/Weapons/SMGs/Hyperion/_Shared/_Design/_Unique/XZ/Balance/Balance_SM_HYP_XZ'),
        ("Zheitsev's Eruption", '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/ZheitsevEruption/Balance/Balance_AR_COV_Zheitsev'),
        ]:
    gun_balances.append((
        label,
        '',
        'Named Weapon',
        balance_name,
        ))

# Hardcodes in case you want to run a subset.
#gun_balances = [
#        #('Auto', '', 'Named Weapon', '/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/AutoAime/Balance/Balance_SR_DAL_AutoAime'),
#        #('Hyper-Hydrator', '', 'Named Weapon', '/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/HyperHydrator/Balance/Balance_PS_MAL_HyperHydrator'),
#        ('Linc', '', 'Named Weapon', '/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/_Unique/Drill/Balance/Balance_PS_ATL_Drill'),
#        ]

# Shields
shield_balances = []
glob_pattern = '/Game/Gear/Shields/_Design/InvBalance/InvBalD_Shield_*_*_*'
pat = re.compile(r'^/Game/Gear/Shields/_Design/InvBalance/InvBalD_Shield_(?P<manufacturer>.*?)_(?P<rarity>\d+_.*?)$')
for obj_name in data.glob(glob_pattern):
    match = pat.match(obj_name).groupdict()
    rarity_lower = match['rarity'].lower()
    if rarity_lower == '01_common':
        rarity = '01/Common'
    elif rarity_lower == '02_uncommon':
        rarity = '02/Uncommon'
    elif rarity_lower == '03_rare':
        rarity = '03/Rare'
    elif rarity_lower == '04_veryrare':
        rarity = '04/Very Rare'
    else:
        raise Exception('Unknown rarity in {}, {}'.format(obj_name, rarity_lower))
    shield_balances.append((
        match['manufacturer'],
        'Shield',
        rarity,
        obj_name,
        ))
shield_balances.sort()
for (sname, sobj) in [
        ("All-in", '/Game/PatchDLC/Dandelion/Gear/Shield/Clover/Balance/InvBalD_Shield_Clover'),
        ("Back Ham", '/Game/Gear/Shields/_Design/_Uniques/BackHam/Balance/InvBalD_Shield_BackHam'),
        ("Band of Sitorak", '/Game/Gear/Shields/_Design/_Uniques/Cyttorak/bALANCE/InvBalD_Shield_Cyttorak'),
        ("Big Boom Blaster", '/Game/Gear/Shields/_Design/_Uniques/BigBoomBlaster/Balance/InvBalD_Shield_LGD_BigBoomBlaster'),
        ("Black Hole", '/Game/Gear/Shields/_Design/_Uniques/BlackHole/Balance/InvBalD_Shield_LGD_BlackHole'),
        ("Deluxe Badass Combustor", '/Game/Gear/Shields/_Design/_Uniques/_XPLootBooster/Balance/InvBalD_Shield_XPLootBooster'),
        ("Double Downer", '/Game/PatchDLC/Dandelion/Gear/Shield/DoubleDowner/Balance/InvBalD_Shield_DoubleDowner'),
        ("Ember's Blaze", '/Game/PatchDLC/Dandelion/Gear/Shield/Ember/Balance/InvBalD_Shield_Ember'),
        ("Front Loader", '/Game/Gear/Shields/_Design/_Uniques/FrontLoader/Balance/InvBalD_Shield_LGD_FrontLoader'),
        ("Frozen Heart", '/Game/Gear/Shields/_Design/_Uniques/Aurelia/Balance/InvBalD_Shield_LGD_Aurelia'),
        ("Frozen Snowshoe", '/Game/PatchDLC/Raid1/Gear/Shields/_HybridLegendary/SlideKickHybrid/SlideKick_FrozenHeart/Balance/InvBalD_Shield_SlideKickFrozenHeart'),
        ("Golden Touch", '/Game/Gear/Shields/_Design/_Uniques/GoldenTouch/Balance/InvBalD_Shield_GoldenTouch'),
        ("Impaler", '/Game/Gear/Shields/_Design/_Uniques/Impaler/Balance/InvBalD_Shield_LGD_Impaler'),
        ("Loop of 4N631", '/Game/Gear/Shields/_Design/_Uniques/LoopOf4N631/Balance/InvBalD_Shield_HYP_LoopOf4N631'),
        ("MSRC Auto-Dispensary", '/Game/Gear/Shields/_Design/_Uniques/Dispensary/Balance/InvBalD_Shield_LGD_Dispensary'),
        ("Mendel's Multivitamin Shield", '/Game/Gear/Shields/_Design/_Uniques/BuriedAlive/Balance/InvBalD_Shield_BuriedAlive'),
        ("Messy Breakup", '/Game/Gear/Shields/_Design/_Uniques/MessyBreakup/bALANCE/InvBalD_Shield_MessyBreakup'),
        ("Moxxi's Embrace", '/Game/Gear/Shields/_Design/_Uniques/MoxxisEmbrace/Balance/InvBalD_Shield_MoxxisEmbrace'),
        ("Mr Caffeine", '/Game/Gear/Shields/_Design/_Uniques/MrCaffeine/Balance/InvBalD_Shield_PAN_MrCaffeine'),
        ("Nova Berner", '/Game/Gear/Shields/_Design/_Uniques/NovaBurner/Balance/InvBalD_Shield_LGD_NovaBurner'),
        ("Re-Charger Berner", '/Game/PatchDLC/Raid1/Gear/Shields/_HybridLegendary/SlideKickHybrid/ReCharger_Berner/InvBalD_Shield_LGD_ReCharger_Berner'),
        ("Re-Charger", '/Game/Gear/Shields/_Design/_Uniques/Re-Charger/Balance/InvBalD_Shield_LGD_ReCharger'),
        ("Re-Router", '/Game/Gear/Shields/_Design/_Uniques/Vamp/Balance/InvBalD_Shield_Legendary_Vamp'),
        ("Rectifier", '/Game/Gear/Shields/_Design/_Uniques/Rectifier/Balance/InvBalD_Shield_LGD_Rectifier'),
        ("Red Card Re-Charger", '/Game/PatchDLC/Raid1/Gear/Shields/_HybridLegendary/SlideKickHybrid/SlideKick_Recharger/InvBalD_Shield_SlideKickRecharger'),
        ("Red Card", '/Game/Gear/Shields/_Design/_Uniques/SlideKick/Balance/InvBalD_Shield_LGD_SlideKick'),
        ("Red Suit", '/Game/Gear/Shields/_Design/_Uniques/Radiate/Balance/InvBalD_Shield_LGD_Radiate'),
        ("Revengenader", '/Game/Gear/Shields/_Design/_Uniques/Revengenader/Balance/InvBalD_Shield_LGD_Revengenader'),
        ("Rico", '/Game/PatchDLC/Dandelion/Gear/Shield/Rico/Balance/InvBalD_Shield_Rico'),
        ("Rough Rider", '/Game/Gear/Shields/_Design/_Uniques/RoughRider/Balance/InvBalD_Shield_LGD_RoughRider'),
        ("Scream of Terror", '/Game/PatchDLC/BloodyHarvest/Gear/Shields/_Design/_Unique/ScreamOfPain/Balance/InvBalD_Shield_ScreamOfTerror'),
        ("Shooting Star", '/Game/Gear/Shields/_Design/_Uniques/ShootingStar/Balance/InvBalD_Shield_LGD_ShootingStar'),
        ("Stop-Gap", '/Game/Gear/Shields/_Design/_Uniques/StopGap/Balance/InvBalD_Shield_LGD_StopGap'),
        ("The Transformer", '/Game/Gear/Shields/_Design/_Uniques/Transformer/Balance/InvBalD_Shield_LGD_Transformer'),
        ("Unpaler", '/Game/Gear/Shields/_Design/_Uniques/Unpaler/Balance/InvBalD_Shield_LGD_Unpaler'),
        ("Version 0.m", '/Game/PatchDLC/Raid1/Gear/Shields/VersionOmNom/Balance/InvBalD_Shield_Legendary_VersionOmNom'),
        ("Ward", '/Game/Gear/Shields/_Design/_Uniques/Ward/Balance/InvBalD_Shield_Ward'),
        ("Whiskey Tango Foxtrot", '/Game/Gear/Shields/_Design/_Uniques/WhiskeyTangoFoxtrot/Balance/InvBalD_Shield_Legendary_WhiskeyTangoFoxtrot'),
        ]:
    shield_balances.append((sname, 'Shield', 'Named Shield', sobj))

# Grenades
grenade_balances = []
glob_pattern = '/Game/Gear/GrenadeMods/_Design/InvBalance/InvBalD_GrenadeMod_*_*_*'
pat = re.compile(r'^/Game/Gear/GrenadeMods/_Design/InvBalance/InvBalD_GrenadeMod_(?P<manufacturer>.*?)_(?P<rarity>\d+_.*?)$')
for obj_name in data.glob(glob_pattern):
    match = pat.match(obj_name).groupdict()
    rarity_lower = match['rarity'].lower()
    if rarity_lower == '01_common':
        rarity = '01/Common'
    elif rarity_lower == '02_uncommon':
        rarity = '02/Uncommon'
    elif rarity_lower == '03_rare':
        rarity = '03/Rare'
    elif rarity_lower == '04_veryrare':
        rarity = '04/Very Rare'
    else:
        raise Exception('Unknown rarity in {}, {}'.format(obj_name, rarity_lower))
    grenade_balances.append((
        match['manufacturer'],
        'Grenade',
        rarity,
        obj_name,
        ))
grenade_balances.sort()
for (gname, gobj) in [
        ("Acid Burn", '/Game/PatchDLC/Dandelion/Gear/Grenade/AcidBurn/Balance/InvBalD_GM_AcidBurn'),
        ("Burning Summit", '/Game/Gear/GrenadeMods/_Design/_Unique/Summit/Balance/InvBalD_GM_Summit'),
        ("Chocolate Thunder", '/Game/Gear/GrenadeMods/_Design/_Unique/JustDeserts/Balance/InvBalD_GM_JustDeserts'),
        ("Chupa's Organ", '/Game/Gear/GrenadeMods/_Design/_Unique/Chupa/Balance/InvBalD_GM_Chupa'),
        ("Diamond Butt Bomb", '/Game/Gear/GrenadeMods/_Design/_Unique/ButtStallion/Balance/InvBalD_GM_ButtStallion'),
        ("ECHO-2", '/Game/Gear/GrenadeMods/_Design/_Unique/EchoV2/Balance/InvBalD_GM_EchoV2'),
        ("EMP", '/Game/Gear/GrenadeMods/_Design/_Unique/EMP/Balance/InvBalD_GM_EMP'),
        ("Elemental Persistent Contact Grenade", '/Game/Gear/GrenadeMods/_Design/_Unique/Mogwai/Balance/InvBalD_GM_Mogwai'),
        ("Epicenter", '/Game/Gear/GrenadeMods/_Design/_Unique/Epicenter/Balance/InvBalD_GM_Epicenter'),
        ("Exterminator", '/Game/Gear/GrenadeMods/_Design/_Unique/BirthdaySuprise/Balance/InvBalD_GM_BirthdaySuprise'),
        ("Fastball", '/Game/Gear/GrenadeMods/_Design/_Unique/Fastball/Balance/InvBalD_GM_TED_Fastball'),
        ("Firestorm", '/Game/Gear/GrenadeMods/_Design/_Unique/FireStorm/Balance/InvBalD_GM_VLA_FireStorm'),
        ("Fungus Among Us", '/Game/Gear/GrenadeMods/_Design/_Unique/Mushroom/Balance/InvBalD_GM_Shroom'),
        ("Ghast Call", '/Game/PatchDLC/BloodyHarvest/Gear/GrenadeMods/_Design/_Unique/FontOfDarkness/Balance/InvBalD_GM_TOR_FontOfDarkness'),
        ("Hex", '/Game/Gear/GrenadeMods/_Design/_Unique/Seeker/Balance/InvBalD_GM_Seeker'),
        ("Hunter-Seeker", '/Game/Gear/GrenadeMods/_Design/_Unique/HunterSeeker/Balance/InvBalD_GM_HunterSeeker'),
        ("It's Piss", '/Game/Gear/GrenadeMods/_Design/_Unique/Piss/Balance/InvBalD_GM_Piss'),
        ("Kryll", '/Game/Gear/GrenadeMods/_Design/_Unique/Kryll/Balance/InvBalD_GM_Kryll'),
        ("Moxxi's Bouncing Pair", '/Game/Gear/GrenadeMods/_Design/_Unique/MoxiesBosom/Balance/InvBalD_GM_PAN_MoxiesBosom'),
        ("NOG Potion #9", '/Game/Gear/GrenadeMods/_Design/_Unique/WizardOfNOG/Balance/InvBalD_GM_WizardOfNOG'),
        ("Nagata", '/Game/Gear/GrenadeMods/_Design/_Unique/Nagate/Balance/InvBalD_GM_Nagate'),
        ("Porcelain Pipe Bomb", '/Game/Gear/GrenadeMods/_Design/_Unique/ToiletBombs/Balance/InvBalD_GM_TOR_ToiletBombs'),
        ("Quasar", '/Game/Gear/GrenadeMods/_Design/_Unique/Quasar/Balance/InvBalD_GM_Quasar'),
        ("Red Queen", '/Game/Gear/GrenadeMods/_Design/_Unique/RedQueen/Balance/InvBalD_GM_RedQueen'),
        ("Rubber Cheddar Shredder", '/Game/Gear/GrenadeMods/_Design/_Unique/CashMoneyPreorder/Balance/InvBalD_GM_CashMoneyPreorder'),
        ("Slider", '/Game/PatchDLC/Dandelion/Gear/Grenade/Slider/Balance/InvBalD_GM_TED_Slider'),
        ("Storm Front", '/Game/Gear/GrenadeMods/_Design/_Unique/StormFront/Balance/InvBalD_GM_StormFront'),
        ("Surge", '/Game/Gear/GrenadeMods/_Design/_Unique/Surge/Balance/InvBalD_GM_Surge'),
        ("Tina's Hippity Hopper", '/Game/Gear/GrenadeMods/_Design/_Unique/HipHop/Balance/InvBalD_GM_TOR_HipHop'),
        ("Tran-fusion", '/Game/Gear/GrenadeMods/_Design/_Unique/TranFusion/Balance/InvBalD_GM_TranFusion'),
        ("Ultraball", '/Game/Gear/GrenadeMods/_Design/_Unique/ToyGrenade/Balance/InvBalD_GM_ToyGrenade'),
        ("Whispering Ice", '/Game/Gear/GrenadeMods/_Design/_Unique/ObviousTrap/Balance/InvBalD_GM_ObviousTrap'),
        ("Widowmaker", '/Game/Gear/GrenadeMods/_Design/_Unique/WidowMaker/Balance/InvBalD_GM_WidowMaker'),
        ]:
    grenade_balances.append((gname, 'Grenade', 'Named Grenade', gobj))

# COMs
com_balances = []
glob_pattern = '/Game/Gear/ClassMods/_Design/BalanceDefs/InvBalD_ClassMod_*_*_*'
pat = re.compile(r'^/Game/Gear/ClassMods/_Design/BalanceDefs/InvBalD_ClassMod_(?P<character>.*?)_(?P<rarity>\d+_.*?)$')
for obj_name in data.glob(glob_pattern):
    match = pat.match(obj_name).groupdict()
    rarity_lower = match['rarity'].lower()
    if rarity_lower == '01_common':
        rarity = '01/Common'
    elif rarity_lower == '02_uncommon':
        rarity = '02/Uncommon'
    elif rarity_lower == '03_rare':
        rarity = '03/Rare'
    elif rarity_lower == '04_veryrare':
        rarity = '04/Very Rare'
    elif rarity_lower == '05_legendary':
        rarity = '05/Legendary'
        print('NOTICE: Skipping base-game Legendary COM {}.  Upper bound on count is >130 trillion (US)'.format(obj_name))
        continue
    else:
        raise Exception('Unknown rarity in {}, {}'.format(obj_name, rarity_lower))
    com_balances.append((
        match['character'],
        'COM',
        rarity,
        obj_name,
        ))
for (cname, cobj) in [
        ("Beastmaster - R4kk P4k", '/Game/PatchDLC/Raid1/Gear/CM/_D/PartSets/_U/BSM/InvBalD_CM_Beastmaster_Raid1'),
        ("Beastmaster - St4ckbot", '/Game/PatchDLC/Dandelion/Gear/CM/_D/PartSets/_U/BSM/InvBalD_CM_Beastmaster_DLC1'),
        ("Gunner - Green Monster", '/Game/PatchDLC/Dandelion/Gear/CM/_D/PartSets/_U/GUN/InvBalD_CM_Gunner_DLC1'),
        ("Gunner - Raging Bear", '/Game/PatchDLC/Raid1/Gear/CM/_D/PartSets/_U/GUN/InvBalD_CM_Gunner_Raid1'),
        ("Operative - Antifreeze", '/Game/PatchDLC/Raid1/Gear/CM/_D/PartSets/_U/OPE/InvBalD_CM_Operative_Raid1'),
        ("Operative - Seein' Dead", '/Game/PatchDLC/Dandelion/Gear/CM/_D/PartSets/_U/OPE/InvBalD_CM_Operative_DLC1'),
        ("Siren - Golden Rule", '/Game/PatchDLC/Dandelion/Gear/CM/_D/PartSets/_U/SRN/InvBalD_CM_Siren_DLC1'),
        ("Siren - Spiritual Driver", '/Game/PatchDLC/Raid1/Gear/CM/_D/PartSets/_U/SRN/InvBalD_CM_Siren_Raid1'),
        ]:
    com_balances.append((cname, 'COM', '05/Legendary', cobj))
com_balances.sort()

# Artifacts
artifact_balances = [
        ('Common', 'Artifact', '01/Common', '/Game/Gear/Artifacts/_Design/BalanceDefs/InvBalD_Artifact_01_Common'),
        ('Uncommon', 'Artifact', '02/Uncommon', '/Game/Gear/Artifacts/_Design/BalanceDefs/InvBalD_Artifact_02_Uncommon'),
        ('Rare', 'Artifact', '03/Rare', '/Game/Gear/Artifacts/_Design/BalanceDefs/InvBalD_Artifact_03_Rare'),
        ('Very Rare', 'Artifact', '04/Very Rare', '/Game/Gear/Artifacts/_Design/BalanceDefs/InvBalD_Artifact_04_VeryRare'),
        ('Legendary', 'Artifact', '05/Legendary', '/Game/Gear/Artifacts/_Design/BalanceDefs/InvBalD_Artifact_05_Legendary'),
        # Not bothering to do anything fancy here since there's so few.
        ("Electric Banjo", 'Artifact', '05/Legendary', '/Game/Gear/Artifacts/_Design/PartSets/Abilities/_Unique/ElectricBanjo/Balance/InvBalD_Artifact_ElectricBanjo'),
        ("Grave", 'Artifact', '05/Legendary', '/Game/Gear/Artifacts/_Design/PartSets/Abilities/_Unique/Grave/Balance/InvBalD_Artifact_Grave'),
        ("Phoenix Tears", 'Artifact', '05/Legendary', '/Game/Gear/Artifacts/_Design/PartSets/Abilities/_Unique/PhoenixTears/Balance/InvBalD_Artifact_PhoenixTears'),
        ("Road Warrior", 'Artifact', '05/Legendary', '/Game/Gear/Artifacts/_Design/PartSets/Abilities/_Unique/RoadWarrior/Balance/InvBalD_Artifact_RoadWarrior'),
        ("Unleash the Dragon", 'Artifact', '05/Legendary', '/Game/Gear/Artifacts/_Design/PartSets/Abilities/_Unique/ElDragonJr/Balance/InvBalD_Artifact_ElDragonJr'),
        ("Vault Hunter's Relic", 'Artifact', '05/Legendary', '/Game/Gear/Artifacts/_Design/PartSets/Abilities/_Unique/VaultHunterRelic/Balance/InvBalD_Artifact_Relic'),
        ]

# Loop through
for (filename, balances, man_col_name, type_col_name, do_anoints, anoint_expansions) in [
        ('gun_counts.csv', gun_balances, 'Manufacturer/Name', 'Gun Type', True, [
            '/Game/PatchDLC/Raid1/Gear/_GearExtension/GParts/GPartExpansion_Weapons_Raid1',
            # Adds nothing, don't bother
            #'/Game/PatchDLC/Dandelion/Gear/_GearExtension/GParts/GPartExpansion_Weapons_Dandelion',
            # Adds a bunch, but only conditionally during Bloody Harvest, so ignore it.
            #'/Game/PatchDLC/BloodyHarvest/Gear/_Design/_GearExtension/GParts/GPartExpansion_Weapons_BloodyHarvest',
            ]),
        ('shield_counts.csv', shield_balances, 'Manufacturer/Name', None, True, [
            '/Game/PatchDLC/Raid1/Gear/_GearExtension/GParts/GPartExpansion_Shields_Raid1',
            # Adds nothing, don't bother
            #'/Game/PatchDLC/Dandelion/Gear/_GearExtension/GParts/GPartExpansion_Shields_Dandelion',
            # Adds a few, but only conditionally during Bloody Harvest, so ignore it.
            #'/Game/PatchDLC/BloodyHarvest/Gear/_Design/_GearExtension/GParts/GPartExpansion_Shields_BloodyHarvest',
            ]),
        ('grenade_counts.csv', grenade_balances, 'Manufacturer/Name', None, True, [
            '/Game/PatchDLC/Raid1/Gear/_GearExtension/GParts/GPartExpansion_Grenades_Raid1',
            # Adds nothing, don't bother
            #'/Game/PatchDLC/Dandelion/Gear/_GearExtension/GParts/GPartExpansion_Grenades_Dandelion',
            # Adds a few, but only conditionally during Bloody Harvest, so ignore it.
            #'/Game/PatchDLC/BloodyHarvest/Gear/_Design/_GearExtension/GParts/GPartExpansion_Grenades_BloodyHarvest',
            ]),
        # COM counts take forever, they're massive (thanks mostly to skill tree parts)
        #('com_counts.csv', com_balances, 'Character/Name', None, False, []),
        ('artifact_counts.csv', artifact_balances, 'Type/Name', None, False, []),
        ]:

    # Create a struct which defines how many extra anointments, beyond the ones already
    # defined, that various balances will receive from part expansions (so far there's
    # only been one "permanent" addition to this, added w/ Maliwan Takedown)
    anointment_additions = {}
    if do_anoints and anoint_expansions:
        for expansion_obj in anoint_expansions:
            # Don't bother error checking on this, just do it.
            exp = data.get_exports(expansion_obj, 'InventoryGenericPartExpansionData')[0]
            num_parts = len(exp['GenericParts']['Parts'])

            # Grab a list of balance collections which define the gear this expansion will act on.
            # We need to use the refs database to find out what's using the main one as a
            # ParentCollection.
            bal_collections = [exp['InventoryBalanceCollection'][1]]
            for (extra, extra_data) in data.get_refs_to_data(bal_collections[0]):
                if extra_data \
                        and extra_data[0]['export_type'] == 'InventoryBalanceCollectionData' \
                        and extra_data[0]['ParentCollection'][1] == bal_collections[0]:
                    bal_collections.append(extra)

            # Create a set() of balances which apply; we have one current example (the AutoAimè)
            # which is specified more than once (inside the same collection, no less), so this
            # way we'll avoid processing them more than once per anointment expansion.
            bal_set = set()
            for bal_collection in bal_collections:
                # Ditto re: errors
                collection = data.get_exports(bal_collection, 'InventoryBalanceCollectionData')[0]
                if 'InventoryBalanceList' in collection:
                    for bal in collection['InventoryBalanceList']:
                        bal_set.add(bal['asset_path_name'].split('.')[0])

            # Now loop through and add in extra parts.
            for bal_name in bal_set:
                if bal_name in anointment_additions:
                    anointment_additions[bal_name] += num_parts
                else:
                    anointment_additions[bal_name] = num_parts

    # Now start processing
    total_count = 0
    total_count_anoint = 0
    print('Processing {}'.format(filename))
    with open(filename, 'w') as odf:

        writer = csv.writer(odf)
        header = [man_col_name]
        if type_col_name:
            header.append(type_col_name)
        header.extend([
            'Rarity',
            'Balance',
            'Count',
            ])
        if do_anoints:
            header.append('Count With Anoints')
        writer.writerow(header)

        for manufacturer, gun_type, rarity, obj_name in balances:

            print('Processing {} {} {} ({})'.format(manufacturer, gun_type, rarity, obj_name))
            bal = BalanceTree(obj_name, data)
            total_count += bal.gun_count()
            if do_anoints:
                total_count_anoint += bal.gun_count(anointment_additions)
                print('  -> {} ({} with anoints)'.format(bal.gun_count(), bal.gun_count(anointment_additions)))
            else:
                print('  -> {}'.format(bal.gun_count()))

            datarow = [manufacturer]
            if type_col_name:
                datarow.append(gun_type)
            datarow.extend([
                rarity,
                obj_name,
                bal.gun_count(),
                ])
            if do_anoints:
                datarow.append(bal.gun_count(anointment_additions))
            writer.writerow(datarow)

            bal = None

        footer_row = ['Total']
        if type_col_name:
            footer_row.append('')
        footer_row.extend([
            '',
            '',
            total_count,
            ])
        if do_anoints:
            footer_row.append(total_count_anoint)
        writer.writerow(footer_row)
        print('')
        if do_anoints:
            print('Total: {} ({} with anoints)'.format(total_count, total_count_anoint))
        else:
            print('Total: {}'.format(total_count))
        print('...done!')

