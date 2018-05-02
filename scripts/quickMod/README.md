# Quick Moderation pyTSon script

<!--You can find a more recent version of this text [here](https://github.com/Bluscream/pyTSon_plugins/tree/master/scripts/quickMod).-->

## Features
This plugin allows you to set hotkeys for
- Restrict the last user that joined your server
- Restrict the last user that joined your channel
- Bans the last user that joined your server
- Bans the last user that joined your channel
- Revoke talk power from the last user that got TP in your channel
- Give the last user that joined your channel a cgid and sgid in certain channels

### Custom Ban integration
If you have [Custom Ban](https://github.com/Bluscream/pyTSon_plugins/tree/master/scripts/customBan) installed and the IP whitelist set up
quickMod will use that whitelist so you don't accidently ban IPs you're not supposed to ban.

## Installation
To install this script follow one of the tutorials on [this page](https://github.com/Bluscream/pyTSon_plugins/#short-tutorial).

## Configuration
You can find settings in `%APPDATA%\TS3Client\plugins\pyTSon\scripts\quickMod\config.ini` (Make sure to close TeamSpeak before editing)

NOTE: Setting normal hotkeys is currently [broken](https://github.com/pathmann/pyTSon/issues/90) in pyTSon.
Until that's fixed just set the hotkeys as commands instead (See screenshots below)

## Showcase
![](https://i.imgur.com/RiFcyD8.png)

![](https://i.imgur.com/hXeC1RH.png)