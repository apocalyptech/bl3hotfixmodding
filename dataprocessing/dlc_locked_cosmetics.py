#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

from bl3data.bl3data import BL3Data

# Given a bunch of customizations, find out which ones are actually locked by some DLC info

custs = [
        '/Game/PatchDLC/Steam/Gear/WeaponTrinkets/WeaponTrinket_SteamPunk',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/Beastmaster/Heads/CustomHead_Beastmaster_CS',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/Beastmaster/Skins/CustomSkin_Beastmaster_CS',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/Gunner/Heads/CustomHead_Gunner_CS',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/Gunner/Skins/CustomSkin_Gunner_CS',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/Operative/Heads/CustomHead_Operative_CS',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/Operative/Skins/CustomSkin_Operative_CS',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/SirenBrawler/Heads/CustomHead_Siren_CS',
        '/Game/PatchDLC/CitizenScience/PlayerCharacters/_Customizations/SirenBrawler/Skins/CustomSkin_Siren_CS',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomHead_Beastmaster_DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomSkin_Beastmaster_DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomHead_Gunner_DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomSkin_Gunner_DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomHead_Operative_DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomSkin_Operative__DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomHead_Siren_DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/_Shared/CustomSkin_Siren__DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC2_01',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC2_02',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC2_03',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC2_04',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/Beastmaster/CustomEmote_Beastmaster_15',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/Beastmaster/CustomEmote_Beastmaster_16',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/Gunner/CustomEmote_Gunner_15',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/Gunner/CustomEmote_Gunner_16',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/Operative/CustomEmote_Operative_15',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/Operative/CustomEmote_Operative_16',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/SirenBrawler/CustomEmote_Siren_15',
        '/Game/PatchDLC/Hibiscus/PlayerCharacters/_Customizations/Emotes/SirenBrawler/CustomEmote_Siren_16',
        '/Game/PatchDLC/Hibiscus/Gear/WeaponTrinkets/_Shared/Trinket_Hibiscus_01_Squidly',
        '/Game/PatchDLC/Hibiscus/Gear/WeaponTrinkets/_Shared/Trinket_Hibiscus_02_Necrocookmicon',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_1',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_2',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_3',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_4',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_5',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_6',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_7',
        '/Game/PatchDLC/Hibiscus/Customizations/RoomDeco/RoomDeco_DLC2_8',
        ]

data = BL3Data()

for cust in custs:
    obj_data = data.get_data(cust)
    for export in obj_data:
        if 'DlcInventorySetData' in export:
            print('{}: {}'.format(cust, export['DlcInventorySetData'][0]))
            break

