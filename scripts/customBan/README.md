# Custom Ban pyTSon script

This script allows you to customize your bans by a lot.
The normal ban dialog is pretty strict (bans uid, ip and hwid) and adding a ban via "Tools" -> "Ban List" -> "Add" is not very fast.
The only current disatvantages are that it can't ban the HWID and can't find the targets IP if he's using TS3Hooks "hide connectioninfo" "feature".

## Features
- Choose what to ban (Any combination of Nickname, UID and IP)
- Instantly see the ISP and location of the target
- Remote Ban templates (reason, duration) and can be predefined and maintained by the server owner (or you, you just have to host it anywhere)
- You can choose the ban template by either typing its start into the combobox or selecting it from the combobox or the list
- Remote IP Whitelist if your server uses proxies to protect certain users from (D)DoS for example
- Adds a "§" infront of the banreason if that starts with a digit

## Installation
To install this script follow one of the tutorials on [this page](https://github.com/Bluscream/pyTSon_plugins/#short-tutorial).

## Configuration
Configuration is mostly done in the ban dialog itself but you have to set the template and whitelist URLs in `%APPDATA%\TS3Client\plugin\pyTSon\scripts\customBan\config.ini` manually (Make sure Teamspeak is closed beforehand!)

## Templates
The whitelist must be a newline seperated textfile, example
```
1.1.1.1
1.1.1.2
1.1.1.3
```
The ban template file must be valid json, example:
```json
{
  "Soundboard": 604800 /*means 7 days*/,
  "Ban Evading": 0 /*means infinite*/
}
```

## Deployment
To deploy it to your moderators you should create a .ts3_plugin file including
- [include/](https://github.com/Bluscream/pyTSon_plugins/tree/master/include)
- the [script itself](https://github.com/Bluscream/pyTSon_plugins/tree/master/scripts/customBan)

and tell your mods they need to install the [latest pyTSon nightly](https://repo.4qt.de/pyTSon/nightlies/latest/) for their system.

You can find an example [here](https://puu.sh/AdP2f/8f9123f539.ts3_plugin) (Just open it as ZIP archive)

## Showcase
![](https://i.imgur.com/o1tlaF7.gif)