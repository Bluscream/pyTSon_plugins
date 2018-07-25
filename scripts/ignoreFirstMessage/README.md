# Anti AFK pyTSon script

This script will reset your `client_idle_time` each `n` seconds while enabled.
The timer is random between `self.interval[currentServerUID][0]` and `self.interval[currentServerUID][1]` in seconds with decimals

## Tutorial
 - To toggle AntiAFK for all tabs click on "Plugins" -> "pyTSon" -> "Toggle Anti AFK"
 - To configure the AFK times edit `antiAFK.interval` in [\_\_init__.py](https://github.com/Bluscream/pyTSon_plugins/blob/master/scripts/antiAFK/__init__.py)
