#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import sys
from bl3data.bl3data import BL3Data

balance_names = [
        # AR
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Clairvoyance/Balance/Balance_AR_JAK_Clairvoyance',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Homicidal/Balance/Balance_AR_COV_Homicidal',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Mutant/Balance/Balance_AR_JAK_Mutant',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Soulrender/Balance/Balance_DAL_AR_Soulrender',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/SparkyBoom/Balance/Balance_AR_COV_SparkyBoom',

        # Pistols
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/BiteSize/Balance/Balance_PS_JAK_BiteSize',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/FrozenDevil/Balance/Balance_PS_MAL_FrozenDevil',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Hydrafrost/Balance/Balance_PS_COV_Hydrafrost',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Kaleidoscope/Balance/Balance_DAL_PS_Kaleidoscope',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/LittleYeeti/Balance/Balance_PS_JAK_LittleYeeti',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/LoveDrill/Balance/Balance_PS_JAK_LoveDrill_Legendary',

        # Shotguns
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Anarchy/Balance/Balance_SG_TED_Anarchy',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Firecracker/Balance/Balance_SG_HYP_Firecracker',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Insider/Balance/Balance_SG_MAL_ETech_Insider',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Omen/Balance/Balance_SG_TED_Omen',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/SacrificalLamb/Balance/Balance_SG_TED_SacrificialLamb',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Shocker/Balance/Balance_SG_Torgue_ETech_Shocker',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/TheCure/Balance/Balance_SG_JAK_TheCure',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/TheNothing/Balance/Balance_SG_MAL_TheNothing',

        # SMGs
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Oldridian/Balance/Balance_SM_HYP_Oldridian',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/SFForce/Balance/Balance_SM_MAL_SFForce',

        # Snipers, though this code doesn't work for them 'cause the name, etc, comes from the Bolt
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/CockyBastard/Balance/Balance_SR_JAK_CockyBastard',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/Skullmasher/Balance/Balance_SR_JAK_Skullmasher',
        #'/Game/PatchDLC/Hibiscus/Gear/Weapon/_Unique/UnseenThreat/Balance/Balance_SR_JAK_UnseenThreat',

        # Mayhem 2.0 weapons
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/Backburner/Balance/Balance_HW_VLA_ETech_BackBurner',
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/DNA/Balance/Balance_SM_MAL_DNA',
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/DoubleTap/Balance/Balance_PS_ATL_DoubleTap',
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/Kaoson/Balance/Balance_SM_DAHL_Kaoson',
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/Monarch/Balance/Balance_AR_VLA_Monarch',
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/Plague/Balance/Balance_HW_TOR_Plague',
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/Reflux/Balance/Balance_SG_HYP_Reflux',
        '/Game/PatchDLC/Mayhem2/Gear/Weapon/_Shared/_Unique/SandHawk/Balance/Balance_SR_DAL_SandHawk',

        ]
if len(sys.argv) > 1:
    balance_names = [sys.argv[1]]

data = BL3Data()

for balance_name in balance_names:

    # Header
    print('')
    print('Balance: {}'.format(balance_name))

    invbal = data.get_exports(balance_name, 'InventoryBalanceData')[0]

    # Loop through to find the first Barrel part
    barrel_name = None
    for part in invbal['RuntimePartList']['AllParts']:
        if 'export' not in part['PartData']:
            if '_Barrel_' in part['PartData'][1]:
                barrel_name = part['PartData'][1]
                break
    if not barrel_name:
        raise Exception('Barrel Not Found!')
    barrel_full = data.get_data(barrel_name)
    barrel = None
    for export in barrel_full:
        if export['export_type'].startswith('BPInvPart'):
            barrel = export
            break
    if not barrel:
        raise Exception('BPInvPart not found for barrel')

    # Grab the name object out of it
    try:
        title_name = barrel['TitlePartList'][0][1]
        title_obj = data.get_exports(title_name, 'InventoryNamePartData')[0]
        title = title_obj['PartName']['string']
    except:
        title = '(no title found, maybe not on barrel?)'

    # And the red text, if we have any
    red_text = None
    try:
        for uistat in barrel['UIStats']:
            if 'RedText' in uistat['UIStat'][1]:
                red_text_name = uistat['UIStat'][1]
                red_text_obj = data.get_exports(red_text_name, 'UIStatData_Text')[0]
                red_text = red_text_obj['Text']['string']
                break
    except:
        red_text_name = '(no red text found, maybe not on barrel?)'
        red_text = '(no red text found, maybe not on barrel?)'

    # Making all kinds of assumptions in here
    print('Name: {}'.format(title))
    if red_text:
        print('Red Text Object: {}'.format(red_text_name))
        print('Red Text: {}'.format(red_text))
    else:
        print('No Red Text')
    print('Rarity: {}'.format(invbal['RarityData'][0]))
    print('Manufacturer: {}'.format(invbal['Manufacturers'][0]['ManufacturerData'][0]))
    print('Type: {}'.format(invbal['GearBuilderCategory'][0]))
    print('')
