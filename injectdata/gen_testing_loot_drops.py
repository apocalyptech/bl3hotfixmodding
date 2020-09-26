#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright 2019-2020 Christopher J. Kucera
# <cj@apocalyptech.com>
# <http://apocalyptech.com/contact.php>
#
# This Borderlands 3 Hotfix Mod is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This Borderlands 3 Hotfix Mod is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this Borderlands 3 Hotfix Mod.  If not, see
# <https://www.gnu.org/licenses/>.

from bl3hotfixmod.bl3hotfixmod import Mod

def set_pool(mod, pool_to_set, balances, char=None):

    parts = []
    for bal in balances:
        if type(bal) is tuple:
            (bal1, bal2) = bal
        else:
            bal1 = bal
            bal2 = bal
        part = '(InventoryBalanceData={},ResolvedInventoryBalanceData={},Weight=(BaseValueConstant=1))'.format(
                Mod.get_full_cond(bal1),
                Mod.get_full_cond(bal2, 'InventoryBalanceData'),
                )
        parts.append(part)
    if char is None:
        hf_subtype = Mod.PATCH
        hf_pkg = ''
    else:
        hf_subtype = Mod.CHAR
        hf_pkg = char
    mod.reg_hotfix(hf_subtype, hf_pkg,
            pool_to_set,
            'BalancedItems',
            '({})'.format(','.join(parts)))

mod = Mod('testing_loot_drops.txt',
        'Testing loot drops...',
        'Apocalyptech',
        [],
        lic=Mod.CC_BY_SA_40,
        )

do_pool_set = True
drop_quantity = 5

# This one's my usual 'rotating' pool that gets used
pool_to_set = '/Game/GameData/Loot/ItemPools/Guns/SniperRifles/ItemPool_SnipeRifles_Legendary'
#pool_to_set = '/Game/GameData/Loot/ItemPools/Guns/Shotguns/ItemPool_Shotguns_Legendary'
#pool_to_set = '/Game/GameData/Loot/ItemPools/Shields/ItemPool_Shields_05_Legendary'
#pool_to_set = '/Game/GameData/Loot/ItemPools/GrenadeMods/ItemPool_GrenadeMods_05_Legendary'
#pool_to_set = '/Game/Gear/Artifacts/_Design/ItemPools/ItemPool_Artifacts_01_Common'
#pool_to_set = '/Game/Gear/Artifacts/_Design/ItemPools/ItemPool_Artifacts_04_VeryRare'
#pool_to_set = '/Game/Gear/Artifacts/_Design/ItemPools/ItemPool_Artifacts_05_Legendary'
#pool_to_set = '/Game/Gear/ClassMods/_Design/ItemPools/ItemPool_ClassMods_05_Legendary'
#pool_to_set = '/Game/Gear/ClassMods/_Design/ItemPools/ItemPool_ClassMods_Beastmaster_05_Legendary'
#pool_to_set = '/Game/Gear/ClassMods/_Design/ItemPools/ItemPool_ClassMods_Gunner_05_Legendary'
#pool_to_set = '/Game/Gear/ClassMods/_Design/ItemPools/ItemPool_ClassMods_Operative_05_Legendary'
#pool_to_set = '/Game/Gear/Artifacts/_Design/ItemPools/ItemPool_Artifacts_03_Rare'
#pool_to_set = '/Game/Gear/Artifacts/_Design/ItemPools/ItemPool_Artifacts'
#pool_to_set = '/Game/GameData/Loot/ItemPools/Shields/ItemPool_Shields_All'
#pool_to_set = '/Game/GameData/Loot/ItemPools/Guns/SMG/ItemPool_SMGs_VeryRare'

# Hoovering up cosmetics
#pool_to_set = '/Game/GameData/Loot/ItemPools/ItemPool_SkinsAndMisc'
#pool_to_set = '/Game/Pickups/Customizations/_Design/ItemPools/Heads/ItemPool_Customizations_Heads_Loot_Siren'
#pool_to_set = '/Game/Pickups/Customizations/_Design/ItemPools/Heads/ItemPool_Customizations_Heads_Loot_Beastmaster'
#pool_to_set = '/Game/Pickups/Customizations/_Design/ItemPools/Skins/ItemPool_Customizations_Skins_Loot_Beastmaster'
#pool_to_set = '/Game/Pickups/Customizations/_Design/ItemPools/Heads/ItemPool_Customizations_Heads_Loot_Gunner'
#pool_to_set = '/Game/Pickups/Customizations/_Design/ItemPools/PlayerRoomDeco/ItemPool_Customizations_RoomDeco_Loot'
#pool_to_set = '/Game/Gear/WeaponTrinkets/_Design/ItemPools/ItemPool_Customizations_WeaponTrinkets_Loot'
#pool_to_set = '/Game/PlayerCharacters/_Customizations/EchoDevice/ItemPools/ItemPool_Customizations_Echo_Loot'
#pool_to_set = '/Game/Gear/WeaponSkins/_Design/ItemPools/ItemPool_Customizations_WeaponSkins_Loot'

balances = [

        # Testing Gear!
        '/Game/PatchDLC/Raid1/Re-Engagement/Weapons/CraderMP5/Balance/Balance_SM_DAHL_CraderMP5',
        '/Game/Gear/Shields/_Design/_Uniques/Transformer/Balance/InvBalD_Shield_LGD_Transformer',

        # Alisma Skins (Bloody Harvest-related)
        # Haunted Look
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Beastmaster/Skins/CustomSkin_Beastmaster_63.InvBal_CustomSkin_Beastmaster_63',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Gunner/Skins/CustomSkin_Gunner_63.InvBal_CustomSkin_Gunner_63',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Operative/Skins/CustomSkin_Operative_63.InvBal_CustomSkin_Operative_63',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/SirenBrawler/Skins/CustomSkin_Siren_63.InvBal_CustomSkin_Siren_63',

        # Alisma Skins
        # Spl4tter
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomSkin_Beastmaster_DLC4_01.InvBal_CustomSkin_Beastmaster_DLC4_01',
        # Splatter
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomSkin_Gunner_DLC4_01.InvBal_CustomSkin_Gunner_DLC4_01',
        # (note the extra underscores on these two!)
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomSkin_Operative__DLC4_01.InvBal_CustomSkin_Operative__DLC4_01',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomSkin_Siren__DLC4_01.InvBal_CustomSkin_Siren__DLC4_01',

        # Alisma Heads
        # Lumin4ry
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomHead_Beastmaster_DLC4_01.InvBal_CustomHead_Beastmaster_DLC4_01',
        # Spark of Genius
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomHead_Gunner_DLC4_01.InvBal_CustomHead_Gunner_DLC4_01',
        # Thinking Clearly
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomHead_Operative_DLC4_01.InvBal_CustomHead_Operative_DLC4_01',
        # Wired Science
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/_Shared/CustomHead_Siren_DLC4_01.InvBal_CustomHead_Siren_DLC4_01',

        # Alisma Room Decorations
        # Memory Orbs
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/RoomDeco/RoomDeco_DLC4_01_Orbs.InvBal_RoomDeco_DLC4_01_Orbs',
        # Psychoreaver Trophy
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/RoomDeco/RoomDeco_DLC4_02_Trophy.InvBal_RoomDeco_DLC4_02_Trophy',
        # Golden Buzz-axe
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/RoomDeco/RoomDeco_DLC4_03_Axe.InvBal_RoomDeco_DLC4_03_Axe',
        # Krieg's Moon
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/RoomDeco/RoomDeco_DLC4_04_Moon.InvBal_RoomDeco_DLC4_04_Moon',
        # Krieg's Mask
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/RoomDeco/RoomDeco_DLC4_05_Mask.InvBal_RoomDeco_DLC4_05_Mask',

        # Alisma Emotes
        # 01: Rage
        # 02: Mindblowing
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/Beastmaster/CustomEmote_Beastmaster_DLC4_01.InvBal_CustomEmote_Beastmaster_DLC4_01',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/Beastmaster/CustomEmote_Beastmaster_DLC4_02.InvBal_CustomEmote_Beastmaster_DLC4_02',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/Gunner/CustomEmote_Gunner_DLC4_01.InvBal_CustomEmote_Gunner_DLC4_01',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/Gunner/CustomEmote_Gunner_DLC4_02.InvBal_CustomEmote_Gunner_DLC4_02',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/Operative/CustomEmote_Operative_DLC4_01.InvBal_CustomEmote_Operative_DLC4_01',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/Operative/CustomEmote_Operative_DLC4_02.InvBal_CustomEmote_Operative_DLC4_02',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/SirenBrawler/CustomEmote_Siren_DLC4_01.InvBal_CustomEmote_Siren_DLC4_01',
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/Emotes/SirenBrawler/CustomEmote_Siren_DLC4_02.InvBal_CustomEmote_Siren_DLC4_02',
        
        # Alisma ECHO Themes
        # Message from Beyond
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_79.InvBal_ECHOTheme_79',
        # Grapevine Hotline
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC4_01.InvBal_ECHOTheme_DLC4_01',
        # Hotwire Handheld
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC4_02.InvBal_ECHOTheme_DLC4_02',
        # Electric Cell
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC4_03.InvBal_ECHOTheme_DLC4_03',
        # Hot and Cold Call
        #'/Game/PatchDLC/Alisma/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_DLC4_04.InvBal_ECHOTheme_DLC4_04',

        # Alisma Trinkets
        # Divergent Thinking
        #'/Game/PatchDLC/Alisma/Gear/WeaponTrinkets/Trinket_DLC4_Trinket_01.InvBal_Trinket_DLC4_Trinket_01',
        # King's Knight
        #'/Game/PatchDLC/Alisma/Gear/WeaponTrinkets/Trinket_DLC4_Trinket_02.InvBal_Trinket_DLC4_Trinket_02',
        # A Shrinking Feeling (Bloody Harvest Related)
        #'/Game/PatchDLC/Alisma/Gear/WeaponTrinkets/_Shared/Trinket_League_BloodyHarvest_2020.InvBal_Trinket_League_BloodyHarvest_2020',

        # Alisma COMs
        # Peregrine
        #'/Game/PatchDLC/Alisma/Gear/ClassMods/_Design/BSM/InvBalD_CM_Beastmaster_Alisma',
        # Flare
        #'/Game/PatchDLC/Alisma/Gear/ClassMods/_Design/GUN/InvBalD_CM_Gunner_Alisma',
        # Hustler
        #'/Game/PatchDLC/Alisma/Gear/ClassMods/_Design/OPE/InvBalD_CM_Operative_Alisma',
        # Muse
        #'/Game/PatchDLC/Alisma/Gear/ClassMods/_Design/SRN/InvBalD_CM_Siren_Alisma',

        # Alisma Shields
        # Faulty Star
        #'/Game/PatchDLC/Alisma/Gear/Shields/_Uniques/FaultyStar/Balance/InvBalD_Shield_Legendary_FaultyStar',
        # Guilty Spark
        #'/Game/PatchDLC/Alisma/Gear/Shields/_Uniques/FaultyStar/Balance/InvBalD_Shield_Legendary_FaultyStar_Epic',
        # Plus Ultra
        #'/Game/PatchDLC/Alisma/Gear/Shields/_Uniques/PlusUltra/Balance/InvBalD_Shield_Legendary_PlusUltra',
        # Limit Break
        #'/Game/PatchDLC/Alisma/Gear/Shields/_Uniques/PlusUltra/Balance/InvBalD_Shield_Legendary_PlusUltra_Epic',

        # Alisma Weapons
        # Ashen Beast
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/AshenBeast/Balance/Balance_SM_DAL_ETech_AshenBeast_Epic',
        # Blood-Starved Beast
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/AshenBeast/Balance/Balance_SM_DAL_ETech_AshenBeast',
        # Minor Kong
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/BanditLauncher/Balance/Balance_HW_COV_BanditLauncher_Epic',
        # Major Kong
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/BanditLauncher/Balance/Balance_HW_COV_BanditLauncher',
        # Blind Bandit
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/BlindBandit/Balance/Balance_SG_MAL_BlindBandit_Epic',
        # Blind Sage
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/BlindBandit/Balance/Balance_SG_MAL_BlindBandit',
        # Reunion
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Convergence/Balance/Balance_SG_HYP_Convergence_Epic',
        # Convergence
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Convergence/Balance/Balance_SG_HYP_Convergence',
        # Likable Rascal
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/LovableRogue/Balance/Balance_AR_TOR_LovableRogue_Epic',
        # Lovable Rogue
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/LovableRogue/Balance/Balance_AR_TOR_LovableRogue',
        # P.A.T. Mk. II
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/PAT_Mk3/Balance/Balance_SM_TED_PatMk3_Epic',
        # P.A.T. Mk. I
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/PAT_Mk3/Balance/Balance_SM_TED_PatMk3_Parent',
        # P.A.T. Mk. III
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/PAT_Mk3/Balance/Balance_SM_TED_PatMk3',
        # Sawpenny
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Sawhorse/Balance/Balance_AR_COV_Sawhorse_Epic',
        # Rebound
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Sawhorse/Balance/Balance_AR_COV_Sawhorse',
        # Septimator
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Septimator/Balance/Balance_VLA_SR_Septimator_Epic',
        # Septimator Prime
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Septimator/Balance/Balance_VLA_SR_Septimator',
        # Critical Mass
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Voice/Balance/Balance_PS_TOR_Voice_Epic',
        # Prompt Critical
        #'/Game/PatchDLC/Alisma/Gear/Weapon/_Unique/Voice/Balance/Balance_PS_TOR_Voice',

        # Atlas Gear (which have multiple tracker types; this isn't exhaustive)
        #'/Game/Gear/Weapons/AssaultRifles/Atlas/_Shared/_Design/Balance/Balance_ATL_AR_01_Common.Balance_ATL_AR_01_Common',
        #'/Game/Gear/Weapons/AssaultRifles/Atlas/_Shared/_Design/Balance/Balance_ATL_AR_02_UnCommon.Balance_ATL_AR_02_UnCommon',
        #'/Game/Gear/Weapons/AssaultRifles/Atlas/_Shared/_Design/Balance/Balance_ATL_AR_03_Rare.Balance_ATL_AR_03_Rare',
        #'/Game/Gear/Weapons/AssaultRifles/Atlas/_Shared/_Design/Balance/Balance_ATL_AR_04_VeryRare.Balance_ATL_AR_04_VeryRare',
        #'/Game/Gear/Weapons/AssaultRifles/Atlas/_Shared/_Design/_Unique/Carrier/Balance/Balance_ATL_AR_Carrier.Balance_ATL_AR_Carrier',
        #'/Game/Gear/Weapons/HeavyWeapons/ATL/_Shared/_Design/BalanceState/Balance_HW_ATL_01_Common.Balance_HW_ATL_01_Common',
        #'/Game/Gear/Weapons/HeavyWeapons/ATL/_Shared/_Design/BalanceState/Balance_HW_ATL_02_UnCommon.Balance_HW_ATL_02_UnCommon',
        #'/Game/Gear/Weapons/HeavyWeapons/ATL/_Shared/_Design/BalanceState/Balance_HW_ATL_03_Rare.Balance_HW_ATL_03_Rare',
        #'/Game/Gear/Weapons/HeavyWeapons/ATL/_Shared/_Design/BalanceState/Balance_HW_ATL_04_VeryRare.Balance_HW_ATL_04_VeryRare',
        #'/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/Balance/Balance_PS_ATL_01_Common.Balance_PS_ATL_01_Common',
        #'/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/Balance/Balance_PS_ATL_02_UnCommon.Balance_PS_ATL_02_UnCommon',
        #'/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/Balance/Balance_PS_ATL_03_Rare.Balance_PS_ATL_03_Rare',
        #'/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/Balance/Balance_PS_ATL_04_VeryRare.Balance_PS_ATL_04_VeryRare',

        # Playing around with modding Maliwan charge times, here's some spawns for Maliwan guns
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/BalanceState/Balance_PS_MAL_04_VeryRare.Balance_PS_MAL_04_VeryRare',
        #'/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/BalanceState/Balance_SG_MAL_04_VeryRare.Balance_SG_MAL_04_VeryRare',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/BalanceState/Balance_SM_MAL_04_VeryRare.Balance_SM_MAL_04_VeryRare',
        #'/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/Balance/Balance_MAL_SR_04_VeryRare.Balance_MAL_SR_04_VeryRare',
        #'/Game/Gear/Weapons/_Shared/_Design/_Manufacturers/_ETech/_Design/Pistol/MAL/Balance/Balance_PS_MAL_ETech_Rare.Balance_PS_MAL_ETech_Rare',
        #'/Game/Gear/Weapons/_Shared/_Design/_Manufacturers/_ETech/_Design/Shotgun/Maliwan/Balance/Balance_SG_MAL_ETech_VeryRare.Balance_SG_MAL_ETech_VeryRare',
        #'/Game/Gear/Weapons/_Shared/_Design/_Manufacturers/_ETech/_Design/SMGs/Maliwan/Balance/Balance_SM_MAL_ETech_VeryRare.Balance_SM_MAL_ETech_VeryRare',
        #'/Game/Gear/Weapons/_Shared/_Design/_Manufacturers/_ETech/_Design/SniperRifles/Maliwan/Balance/Balance_SR_MAL_ETech_VeryRare.Balance_SR_MAL_ETech_VeryRare',

        # Maliwan uniques/legendaries
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/E3/Balance_SM_MAL_E3.Balance_SM_MAL_E3',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/Hellshock/Balance/Balance_PS_MAL_Hellshock.Balance_PS_MAL_Hellshock',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/Plumber/Balance/Balance_PS_MAL_Plumber.Balance_PS_MAL_Plumber',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/ThunderballFist/Balance/Balance_PS_MAL_ThunderballFists.Balance_PS_MAL_ThunderballFists',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/HyperHydrator/Balance/Balance_PS_MAL_HyperHydrator.Balance_PS_MAL_HyperHydrator',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/Starkiller/Balance/Balance_PS_MAL_Starkiller.Balance_PS_MAL_Starkiller',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/SuckerPunch/Balance/Balance_PS_MAL_SuckerPunch.Balance_PS_MAL_SuckerPunch',
        #'/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Recursion/Balance/Balance_SG_MAL_Recursion.Balance_SG_MAL_Recursion',
        #'/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Trev/Balance/Balance_SG_MAL_Trev.Balance_SG_MAL_Trev',
        #'/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Wisp/Balance/Balance_SG_MAL_Wisp.Balance_SG_MAL_Wisp',
        #'/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/MouthPiece2/Balance/Balance_SG_MAL_Mouthpiece2.Balance_SG_MAL_Mouthpiece2',
        #'/Game/Gear/Weapons/Shotguns/Maliwan/_Shared/_Design/_Unique/Shriek/Balance/Balance_SG_MAL_Shriek.Balance_SG_MAL_Shriek',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Cutsman/Balance/Balance_SM_MAL_Cutsman.Balance_SM_MAL_Cutsman',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/DestructoSpin/Balance/Balance_SM_MAL_DestructoSpin.Balance_SM_MAL_DestructoSpin',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Devoted/Balance/Balance_SM_MAL_Devoted.Balance_SM_MAL_Devoted',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/CloudKill/Balance/Balance_SM_MAL_CloudKill.Balance_SM_MAL_CloudKill',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Crit/Balance/Balance_SM_MAL_Crit.Balance_SM_MAL_Crit',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Egon/Balance/Balance_SM_MAL_Egon.Balance_SM_MAL_Egon',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Emporer/Balance/Balance_SM_MAL_Emporer.Balance_SM_MAL_Emporer',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Kevins/Balance/Balance_SM_MAL_Kevins.Balance_SM_MAL_Kevins',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Tsunami/Balance/Balance_SM_MAL_Tsunami.Balance_SM_MAL_Tsunami',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/VibraPulse/Balance/Balance_SM_MAL_VibraPulse.Balance_SM_MAL_VibraPulse',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/westergun/Balance/Balance_SM_MAL_westergun.Balance_SM_MAL_westergun',
        #'/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/ASMD/Balance/Balance_MAL_SR_ASMD.Balance_MAL_SR_ASMD',
        #'/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/Krakatoa/Balance/Balance_MAL_SR_Krakatoa.Balance_MAL_SR_Krakatoa',
        #'/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/Storm/Balance/Balance_MAL_SR_LGD_Storm.Balance_MAL_SR_LGD_Storm',
        #'/Game/Gear/Weapons/SniperRifles/Maliwan/Shared/_Design/_Unique/_Legendary/Soleki/Balance/Balance_MAL_SR_Soleki.Balance_MAL_SR_Soleki',

        # Bloody Harvest rewards:
        #'/Game/PatchDLC/BloodyHarvest/Gear/Weapons/WeaponTrinkets/_Shared/Trinket_League_BloodyHarvest_1.InvBal_Trinket_League_BloodyHarvest_1',
        #'/Game/PatchDLC/BloodyHarvest/PlayerCharacters/_Customizations/EchoDevice/ECHOTheme_11.InvBal_ECHOTheme_11',
        #'/Game/PatchDLC/BloodyHarvest/PlayerCharacters/_Customizations/Beastmaster/Skins/CustomSkin_Beastmaster_40.InvBal_CustomSkin_Beastmaster_40',
        #'/Game/PatchDLC/BloodyHarvest/PlayerCharacters/_Customizations/Gunner/Skins/CustomSkin_Gunner_40.InvBal_CustomSkin_Gunner_40',
        #'/Game/PatchDLC/BloodyHarvest/PlayerCharacters/_Customizations/Operative/Skins/CustomSkin_Operative_40.InvBal_CustomSkin_Operative_40',
        #'/Game/PatchDLC/BloodyHarvest/PlayerCharacters/_Customizations/SirenBrawler/Skins/CustomSkin_Siren_40.InvBal_CustomSkin_Siren_40',
        #'/Game/PatchDLC/BloodyHarvest/Gear/Weapons/WeaponSkins/WeaponSkin_BloodyHarvest_01.InvBal_WeaponSkin_BloodyHarvest_01',

        # Broken Hearts rewards:
        #'/Game/PatchDLC/EventVDay/Gear/Weapon/_Unique/WeddingInvitation/Balance/Balance_SR_JAK_WeddingInvite.Balance_SR_JAK_WeddingInvite',
        #'/Game/PatchDLC/EventVDay/Gear/Weapon/_Unique/TwitchPrime/Balance/Balance_SG_TED_Twitch.Balance_SG_TED_Twitch',
        #'/Game/PatchDLC/EventVDay/Gear/Weapon/_Unique/PolyAim/Balance/Balance_SM_MAL_PolyAim.Balance_SM_MAL_PolyAim',
        #'/Game/PatchDLC/EventVDay/Gear/Weapon/WeaponTrinkets/_Shared/Trinket_League_VDay_1.InvBal_Trinket_League_VDay_1',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/ECHODevice/EchoTheme_Valentines_01.InvBal_EchoTheme_Valentines_01',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomSkin_Beastmaster_50.InvBal_CustomSkin_Beastmaster_50',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomSkin_Gunner_50.InvBal_CustomSkin_Gunner_50',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomSkin_Operative_50.InvBal_CustomSkin_Operative_50',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomSkin_Siren_50.InvBal_CustomSkin_Siren_50',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomHead_BeastMaster_Twitch.InvBal_CustomHead_BeastMaster_Twitch',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomHead_Gunner_Twitch.InvBal_CustomHead_Gunner_Twitch',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomHead_Operative_Twitch.InvBal_CustomHead_Operative_Twitch',
        #'/Game/PatchDLC/EventVDay/PlayerCharacters/_Shared/CustomHead_Siren_Twitch.InvBal_CustomHead_Siren_Twitch',

        # NOG Heads:
        #'/Game/PlayerCharacters/_Customizations/Beastmaster/Heads/CustomHead_Beastmaster_22.InvBal_CustomHead_Beastmaster_22',
        #'/Game/PlayerCharacters/_Customizations/Gunner/Heads/CustomHead_Gunner_22.InvBal_CustomHead_Gunner_22',
        #'/Game/PlayerCharacters/_Customizations/Operative/Heads/CustomHead_Operative_22.InvBal_CustomHead_Operative_22',
        #'/Game/PlayerCharacters/_Customizations/SirenBrawler/Heads/CustomHead_Siren_22.InvBal_CustomHead_Siren_22',

        # Golden weapon skin + trinket.  Technically we already have these, as it turns out, but they're not
        # active unless you actually have the preorder "DLC" or whatever.
        #'/Game/Gear/WeaponSkins/_Design/SkinParts/WeaponSkin_21.InvBal_WeaponSkin_21',
        #'/Game/Gear/WeaponTrinkets/_Design/TrinketParts/WeaponTrinket_51.InvBal_WeaponTrinket_51',

        # Weapons which don't have anointments in the base game
        #'/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/AmazingGrace/Balance/Balance_PS_JAK_AmazingGrace',
        #'/Game/Gear/Weapons/AssaultRifles/Torgue/_Shared/_Design/_Unique/AmberManagement/Balance/Balance_AR_TOR_AmberManagement',
        #'/Game/Gear/Weapons/Pistols/Tediore/Shared/_Design/_Unique/BabyMaker/Balance/Salvage/Balance_PS_Tediore_BabyMaker_Salvage',
        #'/Game/Gear/Weapons/AssaultRifles/Vladof/_Shared/_Design/_Unique/BigSucc/Balance_AR_VLA_BigSucc',
        #'/Game/Gear/Weapons/Shotguns/Torgue/_Shared/_Design/_Unique/Brew/Balance/Balance_SG_TOR_Brewha',
        #'/Game/Gear/Weapons/SniperRifles/Dahl/_Shared/_Design/_Unique/BrashisDedication/Balance/Balance_SR_DAL_BrashisDedication',
        #'/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/Buttplug/Balance/Balance_PS_JAK_Buttplug',
        #'/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/Chad/Balance/Balance_PS_COV_Chad',
        #'/Game/Gear/Weapons/SniperRifles/Vladof/_Shared/_Design/_Unique/Prison/Balance/Balance_VLA_SR_Prison',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Emporer/Balance/Balance_SM_MAL_Emporer',
        #'/Game/Gear/Weapons/Shotguns/Jakobs/_Shared/_Design/_Unique/Fingerbiter/Balance/Balance_SG_JAK_Fingerbiter',
        #'/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/BurgerCannon/Balance/Balance_HW_TOR_BurgerCannon',
        #'/Game/Gear/Weapons/Pistols/Torgue/_Shared/_Design/_Unique/Nurf/Balance/Balance_PS_TOR_Nurf',
        #'/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/HandOfGlory/Balance/Balance_AR_JAK_HandOfGlory',
        #'/Game/Gear/Weapons/HeavyWeapons/ChildrenOfTheVault/_Shared/_Design/_Unique/HotDrop/Balance/Balance_HW_COV_HotDrop',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/HyperHydrator/Balance/Balance_PS_MAL_HyperHydrator',
        #'/Game/Gear/Weapons/SniperRifles/Jakobs/_Shared/_Design/_Unique/IceQueen/Balance/Balance_SR_JAK_IceQueen',
        #'/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/JustCaustic/Balance/Balance_SM_HYP_JustCaustic',
        #'/Game/Gear/Weapons/SniperRifles/Dahl/_Shared/_Design/_Unique/WorldDestroyer/Balance/Balance_SR_DAL_WorldDestroyer',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/Kevins/Balance/Balance_SM_MAL_Kevins',
        #'/Game/Gear/Weapons/Pistols/ChildrenOfTheVault/_Shared/_Design/_Unique/Mouthpiece/Balance/Balance_PS_COV_Mouthpiece',
        #'/Game/Gear/Weapons/Pistols/Vladof/_Shared/_Design/_Unique/TheLeech/Balance/Balance_PS_VLA_TheLeech',
        #'/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/_Unique/Drill/Balance/Balance_PS_ATL_Drill',
        #'/Game/Gear/Weapons/_Shared/NPC_Weapons/Zero/ZeroForPlayer/Balance_SR_HYP_ZeroForPlayer',
        #'/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/PasRifle/Balance/Balance_AR_JAK_PasRifle',
        #'/Game/Gear/Weapons/Pistols/Atlas/_Shared/_Design/_Unique/Warmonger/Balance/Balance_PS_ATL_Warmonger',
        #'/Game/Gear/Weapons/HeavyWeapons/ChildrenOfTheVault/_Shared/_Design/_Unique/PortaPooper/Balance/Balance_HW_COV_PortaPooper',
        #'/Game/Gear/Weapons/HeavyWeapons/Torgue/_Shared/_Design/_Unique/RYNO/Balance/Balance_HW_TOR_RYNO',
        #'/Game/PatchDLC/Dandelion/Gear/Weapon/_Unique/RoboMasher/Balance/Balance_PS_JAK_RoboMasher',
        #'/Game/Gear/Weapons/Pistols/Jakobs/_Shared/_Design/_Unique/SpyRevolver/Balance_PS_JAK_SpyRevolver',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/SuckerPunch/Balance/Balance_PS_MAL_SuckerPunch',
        #'/Game/Gear/Weapons/Pistols/Maliwan/_Shared/_Design/_Unique/Starkiller/Balance/Balance_PS_MAL_Starkiller',
        #'/Game/Gear/Weapons/AssaultRifles/Jakobs/_Shared/_Design/_Unique/TraitorsDeath/Balance/Balance_AR_JAK_TraitorsDeath',
        #'/Game/Gear/Weapons/SniperRifles/Hyperion/_Shared/_Design/_Unique/TwoTime/Balance/Balance_SR_HYP_TwoTime',
        #'/Game/Gear/Weapons/SMGs/Maliwan/_Shared/_Design/_Unique/E3/Balance_SM_MAL_E3',
        #'/Game/PatchDLC/BloodyHarvest/Gear/GrenadeMods/_Design/_Unique/FontOfDarkness/Balance/InvBalD_GM_TOR_FontOfDarkness',

        # Testing my no-Projected-aug mod
        #'/Game/PatchDLC/Dandelion/Gear/Shield/DoubleDowner/Balance/InvBalD_Shield_DoubleDowner',
        #'/Game/PatchDLC/Raid1/Gear/Shields/_HybridLegendary/SlideKickHybrid/ReCharger_Berner/InvBalD_Shield_LGD_ReCharger_Berner',
        #'/Game/Gear/Shields/_Design/_Uniques/Transformer/Balance/InvBalD_Shield_LGD_Transformer',
        #'/Game/Gear/Shields/_Design/_Uniques/Re-Charger/Balance/InvBalD_Shield_LGD_ReCharger',
        #'/Game/Gear/Shields/_Design/_Uniques/FrontLoader/Balance/InvBalD_Shield_LGD_FrontLoader',
        #'/Game/Gear/Shields/_Design/_Uniques/StopGap/Balance/InvBalD_Shield_LGD_StopGap',
        #'/Game/Gear/Shields/_Design/_Uniques/Rectifier/Balance/InvBalD_Shield_LGD_Rectifier',
        #'/Game/Gear/Shields/_Design/_Uniques/MessyBreakup/bALANCE/InvBalD_Shield_MessyBreakup',
        ]

# Set the pool, if we've been told to
if do_pool_set:
    set_pool(mod, pool_to_set, balances)

# Now set everything's drops.
for hf_type, pool in [

        # Base-game stuff
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/Goliath/ItemPoolList_Goliath_Godliath'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/Goliath/ItemPoolList_Goliath_MegaRaging'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/Goliath/ItemPoolList_Goliath_NonEnraging'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/Goliath/ItemPoolList_Goliath_SuperRaging'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/Goliath/ItemPoolList_Goliath_Ultimate'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/ItemPoolList_AnointedEnemyGunsGear'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/ItemPoolList_BadassEnemyGunsGear'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/ItemPoolList_Boss'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/ItemPoolList_MiniBoss'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/ItemPoolList_StandardEnemyGunsandGear'),
        (Mod.CHAR, '/Game/GameData/Loot/ItemPools/ItemPoolList_VaultBossEnemy'),

        # DLC1 (Dandelion) stuff
        (Mod.CHAR, '/Game/PatchDLC/Dandelion/Enemies/Constructor/_Shared/_Design/Balance/ItemPoolList_Constructor'),
        (Mod.CHAR, '/Game/PatchDLC/Dandelion/Enemies/Loader/_Shared/_Design/ItemPools/ItemPoolList_BadassEnemyGunsGearLoader1'),
        (Mod.CHAR, '/Game/PatchDLC/Dandelion/Enemies/Loader/_Shared/_Design/ItemPools/ItemPoolList_StandardEnemyGunsandGearLoader'),
        (Mod.CHAR, '/Game/PatchDLC/Dandelion/GameData/Loot/EnemyPools/ItemPoolList_BadassEnemyGunsGear_Dandelion'),
        (Mod.CHAR, '/Game/PatchDLC/Dandelion/GameData/Loot/EnemyPools/ItemPoolList_StandardEnemyGunsandGear_Dandelion'),
        (Mod.CHAR, '/Game/PatchDLC/Dandelion/GameData/Loot/EnemyPools/ItemPoolList_Boss_Dandelion'),
        (Mod.CHAR, '/Game/PatchDLC/Dandelion/GameData/Loot/EnemyPools/ItemPoolList_MiniBoss_Dandelion'),

        # DLC2 (Hibiscus) stuff
        (Mod.CHAR, '/Game/PatchDLC/Hibiscus/GameData/Loot/EnemyPools/ItemPoolList_BadassEnemyGunsGear_Hibiscus'),
        (Mod.CHAR, '/Game/PatchDLC/Hibiscus/GameData/Loot/EnemyPools/ItemPoolList_Boss_Hibiscus'),
        (Mod.CHAR, '/Game/PatchDLC/Hibiscus/GameData/Loot/EnemyPools/ItemPoolList_MiniBoss_Hibiscus'),
        (Mod.CHAR, '/Game/PatchDLC/Hibiscus/GameData/Loot/EnemyPools/ItemPoolList_StandardEnemyGunsandGear_Hibiscus'),
        
        # DLC3 (Geranium) stuff
        (Mod.CHAR, '/Game/PatchDLC/Geranium/GameData/Loot/EnemyPools/ItemPoolList_BadassEnemyGunsGear_Geranium'),
        (Mod.CHAR, '/Game/PatchDLC/Geranium/GameData/Loot/EnemyPools/ItemPoolList_Boss_Geranium'),
        (Mod.CHAR, '/Game/PatchDLC/Geranium/GameData/Loot/EnemyPools/ItemPoolList_MiniBoss_Geranium'),
        (Mod.CHAR, '/Game/PatchDLC/Geranium/GameData/Loot/EnemyPools/ItemPoolList_StandardEnemyGunsandGear_Geranium'),

        # Trash Piles - this isn't actually *used* by very many things, as it turns out.  Most stuff
        # ends up referencing the ItemPool directly, instead of using this list.
        # NOTE: the quantity specified here doesn't actually seem to show up, in general -
        # I suspect that some of the spawned gear might fall through the ground.
        (Mod.LEVEL, '/Game/GameData/Loot/ItemPools/ItemPoolList_TrashPile'),

        ]:

    mod.reg_hotfix(hf_type, 'MatchAll',
            pool,
            'ItemPools',
            """(
                (
                    ItemPool={},
                    PoolProbability=(
                        BaseValueConstant=1,
                        DataTableValue=(DataTable=None,RowName="",ValueName=""),
                        BaseValueAttribute=None,
                        AttributeInitializer=None,
                        BaseValueScale=1
                    ),
                    NumberOfTimesToSelectFromThisPool=(
                        BaseValueConstant={},
                        DataTableValue=(DataTable=None,RowName="",ValueName=""),
                        BaseValueAttribute=None,
                        AttributeInitializer=None,
                        BaseValueScale=1
                    )
                )
            )""".format(
                Mod.get_full_cond(pool_to_set, 'ItemPoolData'),
                drop_quantity,
                ))

# Since I'm doing it, may as well put in trash piles specifically
# NOTE: the quantity specified here doesn't actually seem to show up, in general -
# I suspect that some of the spawned gear might fall through the ground.
mod.reg_hotfix(Mod.LEVEL, 'MatchAll',
        '/Game/GameData/Loot/ItemPools/ItemPool_TrashPile',
        'BalancedItems',
        """(
            (
                ItemPoolData={},
                Quantity=(BaseValueConstant={})
            )
        )""".format(
            Mod.get_full_cond(pool_to_set, 'ItemPoolData'),
            drop_quantity,
            ))

mod.close()
