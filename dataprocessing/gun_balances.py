#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import re
import sys
import csv
from bl3data.bl3data import BL3Data

data = BL3Data()

# Balances to loop through
balances = []

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
        if 'Fabricator' in obj_name:
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

            rarity = '{} {}'.format(rarity, transforms.get(rarity_suffix.lower(), rarity_suffix))
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
            elif 'firstgun' in lower:
                rarity = '01/Common (Starting Gear)'
            else:
                raise Exception('Unknown rarity in {}'.format(obj_name))

        # Now add it to our list
        balances.append((
            transforms.get(match['manufacturer'].lower(), match['manufacturer']),
            transforms.get(match['guntype'].lower(), match['guntype']),
            rarity,
            obj_name,
            ))

# Sort the list so far
balances.sort()

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
    balances.append((
        label,
        '',
        'Named Weapon',
        balance_name,
        ))

# Loop through
part_cache = {}
title_cache = {}
with open('gun_balances.csv', 'w') as odf:

    writer = csv.writer(odf)
    writer.writerow([
        'Manufacturer',
        'Gun Type',
        'Rarity',
        'Balance',
        'Category',
        'Min Parts',
        'Max Parts',
        'Weight',
        'Part',
        'Dependencies',
        'Excluders',
        ])

    for manufacturer, gun_type, rarity, bal_name in balances:

        # Load ourselves
        bal_obj = data.get_data(bal_name)
        if len(bal_obj) != 1:
            raise Exception('Unknown export count ({}) for: {}'.format(len(bal_obj), bal_name))
        last_bit = bal_name.split('/')[-1]
        bal_data = bal_obj[0]

        # First things first -- the *weights* that get used are the ones from the Balance, so read 'em.
        # We'll use the TOC and assume that it matches the PartSet APLs.
        weights = []
        for toc in bal_data['RuntimePartList']['PartTypeTOC']:
            toc_weights = []
            for part_idx in range(toc['StartIndex'], toc['StartIndex']+toc['NumParts']):
                toc_weights.append(data.process_bvc_struct(bal_data['RuntimePartList']['AllParts'][part_idx]['Weight']))
            weights.append(toc_weights)

        # Load our PartSet
        partset_name = bal_data['PartSetData'][1]
        partset_obj = data.get_data(partset_name)
        if len(partset_obj) != 1:
            raise Exception('Unknown export count ({}) for: {}'.format(len(partset_obj), partset_name))
        partset_data = partset_obj[0]

        # Loop through APL
        seen_labels = set()
        for apl_idx, apl in enumerate(partset_data['ActorPartLists']):
            if 'bEnabled' in apl and apl['bEnabled']:
                if apl['bCanSelectMultipleParts']:
                    parts_min = apl['MultiplePartSelectionRange']['Min']
                    parts_max = apl['MultiplePartSelectionRange']['Max']
                else:
                    parts_min = 1
                    parts_max = 1

                processed_parts = []
                valid_labels = {}
                for part_idx, part in enumerate(apl['Parts']):

                    # Figure out our part name
                    if 'export' in part['PartData']:
                        part_name = 'None'
                    else:
                        part_name = part['PartData'][1]

                    # Populate the cache, if we need to
                    if part_name not in part_cache:
                        if part_name == 'None':
                            part_cache[part_name] = (set(), set(), None)
                        else:
                            excluders = set()
                            dependencies = set()
                            inspection_label = None
                            part_data = data.get_data(part_name)
                            found_export = False
                            for export in part_data:
                                if export['export_type'].startswith('BPInvPart_'):
                                    found_export = True
                                    if 'Excluders' in export:
                                        for excluder in export['Excluders']:
                                            excluders.add(excluder[1])
                                    if 'Dependencies' in export:
                                        for dependency in export['Dependencies']:
                                            dependencies.add(dependency[1])
                                    if 'PartInspectionTitleOverride' in export:
                                        if len(export['PartInspectionTitleOverride']) > 1:
                                            print('WARNING: Longer name array in {}'.format(part_name))
                                        title_name = export['PartInspectionTitleOverride'][0][1]
                                        if title_name not in title_cache:
                                            title_obj = data.get_data(title_name)
                                            if len(title_obj) != 1:
                                                raise Exception('Unknown export length ({}) for {}'.format(len(title_obj), title_name))
                                            title_cache[title_name] = re.sub(r'\[/?.*?\]', '', title_obj[0]['Text']['string'])

                                            # Some hardcoded overrides
                                            if title_cache[title_name].startswith('TRACKING '):
                                                title_cache[title_name] = 'TRACKING METHOD'
                                            elif title_cache[title_name].endswith(' SHIELD'):
                                                title_cache[title_name] = 'SHIELD TYPE'
                                            elif title_cache[title_name].endswith(' MODULE'):
                                                title_cache[title_name] = 'RELOAD TYPE'
                                            elif title_cache[title_name].startswith('UNDERBARREL '):
                                                title_cache[title_name] = 'UNDERBARREL TYPE'

                                        inspection_label = title_cache[title_name]

                                    # More hardcodes.  The material ones (apart from the general matches on the first
                                    # line) are sort of just guesses, but whatever.  The guns wouldn't otherwise
                                    # have a dedicated material part, so it's probably right.
                                    elif 'material' in part_name.lower() or '_Mat_' in part_name or '_MAT_' in part_name \
                                            or part_name.endswith('/Part_SR_DAL_WorldDestroyer') \
                                            or part_name.endswith('/Part_SR_HYP_Masterwork') \
                                            or part_name.endswith('/Part_SR_HYP_ZeroForPlayer') \
                                            or part_name.endswith('/Part_SR_HYP_Tankman') \
                                            or part_name.endswith('/Part_SR_JAK_IceQueen') \
                                            or part_name.endswith('/Part_SR_HYP_Woodblocks'):
                                        inspection_label = 'MATERIAL'
                                    elif 'FrontSight' in part_name:
                                        inspection_label = 'FRONT SIGHT'
                                    elif 'SlideCap' in part_name:
                                        inspection_label = 'CAPS'
                                    elif 'Underbarrel' in part_name:
                                        inspection_label = 'UNDERBARREL TYPE'
                                    elif 'Magazine' in part_name or '_Mag_' in part_name:
                                        inspection_label = 'MAGAZINE'
                                    elif 'TheWave' in part_name:
                                        inspection_label = 'TK WAVE'
                                    elif '_Sight_' in part_name:
                                        inspection_label = 'SIGHT'
                                    elif part_name.endswith('_BoomSickle'):
                                        inspection_label = 'BOOM SICKLE'
                                    elif part_name.endswith('_Trigger_Fingerbiter') \
                                            or part_name.endswith('_Trigger_Hellwalker'):
                                        inspection_label = 'BODY ACCESSORY'
                                    elif part_name.endswith('/Part_AR_COV_ScopeMount'):
                                        inspection_label = 'RAIL'
                                    elif part_name.endswith('/Part_SG_JAK_Body') \
                                            or part_name.endswith('/Part_PS_MAL_Body') \
                                            or part_name.endswith('/Part_PS_VLA_Body'):
                                        inspection_label = 'BODY'
                                    break
                            if not found_export:
                                raise Exception('Could not find export for {}'.format(part_name))
                            part_cache[part_name] = (excluders, dependencies, inspection_label)

                    # Read from Cache
                    (excluders, dependencies, inspection_label) = part_cache[part_name]
                    processed_parts.append((part_name, excluders, dependencies, inspection_label, apl_idx, part_idx))
                    if inspection_label:
                        if inspection_label in valid_labels:
                            valid_labels[inspection_label] += 1
                        else:
                            valid_labels[inspection_label] = 1

                # Special case!  A partset with literally just *one* part, with a name of None.
                # No reason to show this, has no actual bearing on the weapon.
                if len(processed_parts) == 1 and processed_parts[0][0] == 'None':
                    continue

                # Figure out what the main label should be for this part type
                label_text = '(unknown)'
                label_max = -1
                contention = False
                for label, count in valid_labels.items():
                    if count > label_max:
                        contention = False
                        label_max = count
                        label_text = label
                    elif count == label_max:
                        contention = True

                # Hardcoded fixes.  Grr.
                if contention:
                    if partset_name == '/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/Nurf/Balance/PartSet_PS_TOR_Nurf' and apl_idx == 1:
                        # BODY ACCESSORY vs. BARREL ACCESSORY
                        contention = False
                        label_text = 'BODY ACCESSORY'
                    elif partset_name == '/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/Ogre/Balance/InvPart_VLA_AR_Ogre' and apl_idx == 10:
                        # IRON SIGHTS vs. RAIL
                        contention = False
                        label_text = 'RAIL'

                if contention:
                    raise Exception('Contention in {}, APL {}: {}'.format(partset_name, apl_idx, valid_labels))

                # Make sure we're not re-using a label
                idx = 1
                label_base = label_text
                while label_text in seen_labels:
                    idx += 1
                    label_text = '{} {}'.format(label_base, idx)
                seen_labels.add(label_text)

                for (part_name, excluders, dependencies, _, apl_idx, part_idx) in processed_parts:
                    writer.writerow([
                        manufacturer,
                        gun_type,
                        rarity,
                        bal_name.split('/')[-1],
                        label_text,
                        parts_min,
                        parts_max,
                        weights[apl_idx][part_idx],
                        part_name.split('/')[-1],
                        ', '.join(sorted([d.split('/')[-1] for d in dependencies])),
                        ', '.join(sorted([e.split('/')[-1] for e in excluders])),
                        ])

    print('Done!')

