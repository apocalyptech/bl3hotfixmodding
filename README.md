Borderlands 3 Hotfix-Based Modding
==================================

There is no traditional modding in BL3 (as of April 2, 2020) like there
is for BL2/TPS.  In the meantime, though, while that's being figured out,
there is *technically* a method which could be used by enterprising and
technically savvy would-be modders: intercepting the GBX-provided
hotfixes as they're sent from the servers, and injecting your own
modifications.

This page won't go into details on how exactly to accomplish the first
bit (namely, intercepting the hotfixes).  Given the nature of this
activity, anyone attempting to do so should at least have the ability
to learn how to do it on your own.  There are many utilities out there
which are geared to this kind of on-the-wire editing, such as
[Charles](https://www.charlesproxy.com/), or the one I use,
[mitmproxy](https://mitmproxy.org/).

Remember that there's two components to successfully deploying a
MITM against yourself:

1. Intercepting the network traffic itself
2. Making sure the MITM'd app trusts the SSL cert that you're using
   to do the interception

Pay particular attention to point number 2, and make sure you
understand the security ramifications of what you're doing.  Ideally
your trust alterations are being done in as targetted a manner as
possible.  If you want to get real specific, the one hostname you'd
want to look into is `discovery.services.gearboxsoftware.com`.

Note that Epic Games Store itself does *not* like being MITM'd; they're
probably doing at least some SSL pinning or other techniques to prevent
that kind of thing.  If EGS doesn't auth to Epic properly, it'll launch
BL3 in an "offline" mode and BL3 won't even attempt to try and load
hotfixes, so you'll have to make sure that you're only working with the
BL3 process itself.  Since I have no real interest in doing anything
with the Epic traffic anyway, I've never taken a closer look to try and
get around that, though I *wasn't* successful in getting BL3 to launch
in a mode which asks for hotfixes when EGS considers itself offline.

So: before going any further in here, make sure you've at least got
that much already working.  BL3 should be asking for hotfixes, and
your stuff should be intercepting that traffic enroute, with the
capability to alter it before it makes it back to the game.

Some Hotfix Details
-------------------

The next step, then, is to actually start altering hotfixes, or
at least adding your own.  If you take a look at the data being
sent over from GBX to the game, it's just
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

Modifying the Hotfixes with mitmproxy
-------------------------------------

mitmproxy provides a very handy programmatic API, in Python, which
you can use to process streams that you've intercepted, which is
what I ended up using to make injection pretty easy on myself.
Specifically, I'm using mitmproxy's `mitmdump` command, with a
`-s hfinject.py` argument so that it uses my hotfix injection code.

What `hfinject.py` does is it first looks for a file called
`hfinject.ini`, which is pretty basic and should look like this:

    [main]
    ModDir = injectdata

There's an example stored here as `hfinject.ini.example`.  If
`hfinject.ini` isn't found, the app will create one with those
exact contents.

Then, the app looks inside the directory specified by `ModDir`
for a file named `modlist.txt`, which can look like this:

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
menu to revert back to showing the Borderlands logo, logging you
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

Note that that quick disconnect generally does *not* happen
on the very first hotfix load, though.  Or at least not nearly
as quickly.

Mods
----

A shared collection of BL3 Hotfix mods is now becoming available
at: https://github.com/BLCM/bl3mods

An easier way to browse that collection is with the Borderlands 3
ModCabinet wiki, which lets you browse mods by type:
https://github.com/BLCM/bl3mods/wiki

When Shift Is Down
------------------

Shift had an outage earlier today and I took some initial stabs at
"fully" pretending to be GBX, so that I could still have hotfixes even
in the absence of GBX's services.  You can check those attempts out
at `hfspoof_discovery.py` and `hfspoof_account.py`, though I didn't
actually get them working.  The game seems to make/receive all the
proper calls, but just hangs there forever at the logging-in step.
Perhaps I'll get around to dusting that off at some point...

License
-------

All the code in this project is licensed under the
[GPLv3 or later](https://www.gnu.org/licenses/quick-guide-gplv3.html).
See [COPYING.txt](COPYING.txt) for the full text of the license.

