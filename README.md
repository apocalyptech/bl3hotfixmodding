Borderlands 3 (and Wonderlands) Hotfix-Based Modding (Legacy/Linux)
===================================================================

**Note:** You almost certainly want to be using
[c0dycode's B3HM (Borderlands 3 Hotfix Merger)](https://www.nexusmods.com/borderlands3/mods/244)
instead of this code!  Check [borderlandsmodding.com](http://borderlandsmodding.com/bl3-running-mods/)
for more information on setting up B3HM.

This repo contains a [mitmproxy](https://mitmproxy.org/)-based method of
hotfix injection for Borderlands 3 and Tiny Tina's Wonderlands.  This was
developed and primarily run on Linux, though it can be run on Windows
with a bit of perseverance, too ([WSL](https://docs.microsoft.com/en-us/windows/wsl/install)
is probably the easiest way to run it on Windows).  It basically just
listens for the game's request for hotfixes, and injects your own on
the wire, as if they were sent by GBX.

The main trouble with running this is related to certificate trust issues.
When running BL3 on Linux, some basic system CA-cert manipulation is enough
for the game to trust mitmproxy, but Windows users will likely run into
trust issues.  For Wonderlands, even Linux hosts will run into cert
trust issues, too -- Wonderlands seems to do some more thorough cert
pinning or something.  This page won't go into details on how to bypass those
problems (partially just because I don't *really* know how to do it,
myself).  So, be prepared for that, if you decide to use this.

This page also won't really go into detail on the full setup required to
run this, but in brief:

1. It's probably easiest to use an `/etc/hosts` entry to point the DNS
   name `discovery.services.gearboxsoftware.com` to your machine/VM/whatever
   running mitmproxy.  Note that mitmproxy itself would need to know the
   correct IP for the host.
2. The most handy commandline to launch the script is:
   `mitmdump --certs yourcert.pem -m reverse:https://discovery.services.gearboxsoftware.com/ --listen-host x.x.x.x -p 443 -s hfinject.py`

(you may want to use `-v` and/or `--showhost` as well, when running)

Modifying the Hotfixes with hfinject.py
---------------------------------------

mitmproxy provides a very handy programmatic API, in Python, which
you can use to process streams that you've intercepted.  That's what
I ended up using to make injection pretty easy on myself, in the
`hfinject.py` script.  (See above for a commandline to use it via
mitmproxy.)

What `hfinject.py` does is it first looks for a file called
`hfinject.ini`, which is pretty basic and should look like this:

    [main]
    moddir_bl3 = injectdata_bl3
    moddir_wl = injectdata_wl

There's an example stored here as `hfinject.ini.example`.  If
`hfinject.ini` isn't found, the app will create one with those
exact contents.  It's fine if you don't have both defined, of
course, if you're only going to use this for a single game.

(**Note:** Prior to July 8, 2022, the file only contained a single
`moddir` entry, which was used for Borderlands 3.  On that date,
though, the behavior was changed to have separate directories for
BL3 and WL.  You'll have to update your `hfinject.ini` with the
new syntax, if you've been using this in the past and update to
the new code.)

Then, the app looks inside the directory specified by `moddir_bl3`
or `moddir_wl` (depending on which game requested hotfixes) for a
file named `modlist.txt`, which can look like this:

    # Gearbox Event Recreations
    better_rare_spawn_hunt.txt
    better_eridium_event.txt

    # Cheaper SDUs
    cheaper_sdus.txt

    # Better Loot, in a subdirectory
    other_mods/Apocalyptech/better_loot.txt

    # An absolute path
    /usr/local/even_more_mods/omega_mod.txt

    # If on Windows, you might have an absolute path like:
    C:\Mods\another_mod.txt

    # You can also include other files, if you want:
    !include other_modlist.txt

    # ... and use absolute paths there, too.
    !include C:\Mods\more_modlists.txt

As you can see, lines can be commented using a hash (`#`) sign,
and blank lines are ignored.  Each other non-commented line
should be a name of a mod that you want to load.  If the mod
file is given as a relative path (as it is for all but the last
two in the example above), they will be loaded relative to the
`modlist.txt` file itself.  So in the above example, the mods
`better_rare_spawn_hunt.txt`, `better_eridium_event.txt`, and
`cheaper_sdus.txt` will be right alongside `modlist.txt`.  There
will also be an `other_mods` directory alongside that file,
which will eventually lead to the Better Loot mod.

As seen in the example, you can also just specify absolute paths
to mod files, if you prefer.

Also as seen in the example, you can use `!include` to also read
in other mod listings, to make it easier to enable/disable groups
of mods all at once.  You can comment out those `!include`
lines as per usual with a hash (`#`) mark.

For the mod files themselves, I didn't care enough to do too
much abstraction, so they are very nearly just the raw hotfix
format.  For instance, `cheaper_sdus.txt` just starts like this:

    ###
    ### Name: Cheaper SDUs
    ### Version: 1.0.0
    ### Author: Apocalyptech
    ### Categories: cheat, economy
    ###
    ### License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
    ### License URL: https://creativecommons.org/licenses/by-sa/4.0/
    ###

    ###
    ### Makes the purchaseable SDUs in the game significantly cheaper.
    ###
    ### Generated by gen_cheaper_sdus.py
    ###

    SparkPatchEntry,(1,2,0,),/Game/Pickups/SDU/Table_SDU_AssaultRifle.Table_SDU_AssaultRifle,Lv1,SDUPrice,0,,500

As you can see, the hotfix line itself is practically identically
identical to the "raw" hotfix format, though it's prefixed by
an additional field, which is `SparkPatchEntry` for this one.

As with `modlist.txt`, if a mod file itself changes, `hfinject.py`
will automatically re-load it when the next hotfix verification
happens.

Note that you should **not** escape quote marks in the hotfixes
you put in the mod files -- if you look at the raw JSON data,
you'll see that quotes are escaped, since they're inside of
JSON strings, but `hfinject.py` will take care of doing that
escpaing for you.

Triggering Hotfix Reloads
-------------------------

The quickest way to have the game re-load hotfixes from the server
is to head out to the main menu, hit `Quit`, and then select
`Title Screen` rather than `Desktop`.  That'll cause the main
menu to revert back to showing the Borderlands/Wonderlands logo, logging you
back in to Shift, and then panning down to the usual waiting screen.
Within a few seconds the game should have reloaded hotfixes.
(If using mitmproxy, it's easy to look at its output to know for
sure whether or not the hotfixes have been requested.)

Note that when re-loading hotfixes like that, the game tends to
disconnect from shift within a few seconds, after getting the
hotfix data.  If you look at your mitmdump console output, you'll
see a couple of log lines like:

    x.x.x.x:41818: serverdisconnect
    x.x.x.x:41818: clientdisconnect

If you **don't** see those lines after a few seconds, it
sometimes means that you've screwed up some hotfix syntax
somewhere, and the hotfixes which were sent over to the game
haven't been fully loaded in yet.  So I'll often wait to see
those disconnect notices before proceeding to testing the mods.
Note that Wonderlands seems to take longer before disconnecting
than BL3 did.

Note that that quick disconnect generally does *not* happen
on the very first hotfix load, though.  Or at least not nearly
as quickly.

Mods
----

A shared collection of BL3 Hotfix mods is now becoming available
at: https://github.com/BLCM/bl3mods - There is not currently any
public mod collection for Wonderlands.

An easier way to browse that collection is with the Borderlands 3
ModCabinet wiki, which lets you browse mods by type:
https://github.com/BLCM/bl3mods/wiki

Some Hotfix Details
-------------------

If you take a look at the data being sent over from GBX to the game, it's just
[JSON](https://en.wikipedia.org/wiki/JSON), and there's basically
just one big array which would need to be added to, if you want
to add your own hotfixes.  Each hotfix has a unique `key`, which
also defines when exactly the hotfix will be run, and a `value`,
which is the hotfix itself.

If you already know how BL2/TPS hotfixes work on the backend,
the BL3 hotfixes will seem reasonably familiar.  Some documentation
on the BL2/TPS hotfixes can be found on the BLCMods wiki on a
few pages: [Tutorial: Hotfix Data](https://github.com/BLCM/BLCMods/wiki/Tutorial:-Hotfix-Data#internal-structure)
and [Anatomy of a Mod File](https://github.com/BLCM/BLCMods/wiki/Anatomy-of-a-Mod-File#hotfixes).

There's definitely some differences for the BL3 versions, though,
and I've been starting to document those on the BLCMods wiki as
well: [Borderlands 3 Hotfixes](https://github.com/BLCM/BLCMods/wiki/Borderlands-3-Hotfixes).
You'll want to take a look through there to get a feel for what
hotfixes look like, because if you're constructing them by hand
you'll need to know what they look like.

As for actually writing mods for Borderlands 3, there's a few
newish pages on the BLCM wiki which goes into looking at BL3
data and what we currently know about writing these hotfixes:

 - [Accessing Borderlands 3 Data](https://github.com/BLCM/BLCMods/wiki/Accessing-Borderlands-3-Data)
 - [Borderlands 3 Hotfix Modding](https://github.com/BLCM/BLCMods/wiki/Borderlands-3-Hotfix-Modding)

When Shift Is Down
------------------

I've taken some initial stabs at "fully" pretending to be GBX, so that I could
still have hotfixes even in the absence of GBX's services (such as during a
Shift outage).  You can check those attempts out at `hfspoof_discovery.py` and
`hfspoof_account.py`, though I didn't actually get them working.  The game
seems to make/receive all the proper calls, but just hangs there forever at the
logging-in step.  Perhaps I'll get around to dusting that off at some point...

License
-------

All the code in this project is licensed under the
[GPLv3 or later](https://www.gnu.org/licenses/quick-guide-gplv3.html).
See [COPYING.txt](COPYING.txt) for the full text of the license.

