import ts3lib, ts3defines
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion, getPluginPath
from bluscream import timestamp
from PythonQt.QtCore import QTimer
from devtools import PluginInstaller, installedPackages
from os import walk, listdir, path
from traceback import format_exc

def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(path.sep)
    assert path.isdir(some_dir)
    num_sep = some_dir.count(path.sep)
    for root, dirs, files in walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

class aaa_requirements(ts3plugin):
    name = "aaa_requirements"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "Auto-installs requirements.txt from script directories"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = []
    hotkeys = []
    to_install = []
    installer = None
    auto_update_pip = True

    def __init__(self):
        self.installer = PluginInstaller(self.print_msg)
        # if self.auto_update_pip: self.to_install.append("--upgrade pip")
        _installed = installedPackages()
        installed = []
        for package in _installed:
            name = package["name"]
            if not name in installed: installed.append(name)
        """
        dir = listdir(getPluginPath("scripts"))
        print(dir)
        """
        # noinspection PyTypeChecker
        for subdir, dirs, files in walklevel(getPluginPath("scripts"), 1):
            for file in files:
                file_lower = file.lower()
                if not file_lower.endswith(".txt"): continue
                if file_lower == "requirements.txt":
                    requirements = []
                    # noinspection PyArgumentList
                    with open(path.join(subdir, file), encoding="utf-8") as f:
                        requirements = [line.strip() for line in f.readlines()]
                    if len(requirements) < 1: continue
                    for requirement in requirements:
                        requirement_stripped = self.strip(requirement)
                        if requirement in self.to_install: continue
                        if requirement_stripped in installed: continue
                        try: __import__(requirement_stripped)
                        except ImportError:
                            self.to_install.append(requirement)
                    break
        if len(self.to_install) > 0:
            ts3lib.printMessageToCurrentTab("[color=red]Found missing dependencies %s in \"requirements.txt\" files from scrips, installing..."%self.to_install)
            QTimer.singleShot(0, self.install)
        if PluginHost.cfg.getboolean("general", "verbose"):
            ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def strip(self, requirement):
        if requirement.startswith("-e "): requirement = requirement.replace("-e ", "", 1)
        if requirement.endswith(".git"): requirement = requirement.replace(".git", "", 1)
        for prefix in ["hg", "svn", "bzr", "git"]:
            if requirement.startswith("%s+"%prefix):
                requirement = requirement.rsplit('/',1)[1]
        return requirement

    def install(self, to_install=to_install):
        result = self.installer.installPackages(to_install)
        if not result: ts3lib.printMessageToCurrentTab("[color=red]Failed to install %s!" % to_install)
        self.to_install = []

    def stop(self):
        if hasattr(self, "installer"): del self.installer

    def print_msg(self, msg):
        ts3lib.printMessageToCurrentTab(str(msg.decode('ascii')))