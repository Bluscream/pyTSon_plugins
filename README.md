# Bluscream's pyTSon Scripts
This repository contains [pyTSon](https://github.com/pathmann/pyTSon) scripts that we're either created or modified by me.
For a list of all the scripts available check the [scripts](https://github.com/Bluscream/pyTSon_plugins/tree/master/scripts) subdirectory.

Some of the scripts i created require special dependencies. So if you want a script to run smoothly run make sure that you have up-to-date versions of all the possible requirements.

## Short Tutorial
1. Uninstall your old pyTSon version if you already have it installed via "Tools" -> "Options" -> "Addons" -> "Plugins" -> `pyTSon` -> "Uninstall"
2. Close your Teamspeak Client and make sure no `ts3client_*.exe` is running in your Task Manager
3. Download and install the latest pyTSon nightly for your system from https://repo.4qt.de/pyTSon/nightlies/latest/
4. Download the latest version of this repository from https://github.com/Bluscream/pyTSon_plugins/archive/master.zip
5. Extract the `include/` folder from the ZIP to `%APPDATA%/TS3Client/plugins/pyTSon/` so windows asks you to merge them
6. Extract **only** the scripts you need from `master.zip/scripts` to `%APPDATA%/TS3Client/plugins/pyTSon/scripts/`
7. Make sure "Accept different API Versions" is checked in "Plugins" -> "pyTSon" -> "Settings"
8. Restart your Teamspeak client
9. Open the pyTSon settings dialog via "Plugins" -> "pyTSon" -> "Settings" and check all the scripts that you want.
10. Eventually the scripts have settings so make sure to adjust them by clicking on the cog wheel next to them!
11. If any of the scripts use menuItems you need to restart your client after activating them before you can see their menus.

## Long Tutorial
In case the short tutorial didn't work for you or if you want more indepth informations i provided a more detailed tutorial series on YouTube.
You can find it at https://r4p3.net/resources/pytson.170/field?field=faq!

## FAQ
- I have questions / problems with pyTSon!
  - First check if your issue was already reported [here](https://github.com/pathmann/pyTSon/issues?utf8=%E2%9C%93&q=is%3Aissue) and if not create a new issue for it [here](https://github.com/pathmann/pyTSon/issues/new).
- I have questions / problems with your script!
  - First check if your issue was already reported [here](https://github.com/Bluscream/pyTSon_plugins/issues?utf8=%E2%9C%93&q=is%3Aissue) and if not create a new issue for it [here](https://github.com/Bluscream/pyTSon_plugins/issues/new).
- What is pyTSon?
  - [pyTSon](https://github.com/pathmann/pyTSon) is a python and Qt wrapper for the [[C] Teamspeak 3 Client Plugin API](https://github.com/TeamspeakDocs/PluginAPI) created by [pathmann](https://github.com/pathmann).
- What Teamspeak style are you using?
  - [teamspeak-dark](https://github.com/randomhost/teamspeak-dark) by [randomhost](https://github.com/randomhost).
- Which screenshot tool are you using?
  - [ShareX](https://github.com/ShareX/ShareX) by [Jaex](https://github.com/Jaex).
- Which app do you use for editing `.ui` files?
  - [Qt Designer / Qt Creator](https://www.qt.io/download-qt-installer).
- Which IDE do you use for Python code?
  - [PyCharm](https://www.jetbrains.com/pycharm)
- Is there any tutorial for how to make pyTSon plugins?
  - Yes, [here](https://github.com/pathmann/pyTSon#how-to-develop-a-python-plugin) and [here](https://github.com/pathmann/pyTSon/issues?q=is%3Aissue+is%3Aclosed+label%3Aquestion). If that doesn't help you look through other scripts that you can find. If even that doesn't help just ask [here](https://github.com/Bluscream/pyTSon_plugins/issues/new) or [here](https://github.com/pathmann/pyTSon/issues/new).