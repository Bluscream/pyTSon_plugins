import ts3lib, ts3defines
from os import path
from ts3plugin import ts3plugin, PluginHost
from PythonQt.QtCore import QUrl
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from traceback import format_exc
from pytson import getCurrentApiVersion
from json import loads, dumps
from bluscream import timestamp, clientURL
from re import match, compile, finditer, IGNORECASE
from concurrent.futures import ThreadPoolExecutor

def parseURLs(text:str, pattern):
    urls = []
    for m in finditer(pattern, text):
        if m.group(1) is None:
            urls.append((m.group(4), m.group(3)))
        elif m.group(3) is None:
            urls.append((m.group(2), m.group(1)))
    return urls

def parse_attributes_for_report(wot_report_dict):
    result = {}
    if "0" in wot_report_dict:
        overall = wot_report_dict["0"]
        result["trustworthiness_level"] = __process_value(overall[0])+"[/color]"
        result["trustworthiness_confidence"] = __process_value(overall[1])+"[/color]"
    if "categories" in wot_report_dict:
        categories = wot_report_dict["categories"]
        __process_category(categories, result, "101", "malware_viruses_confidence")
        __process_category(categories, result, "102", "poor_experience_confidence")
        __process_category(categories, result, "103", "phishing_confidence")
        __process_category(categories, result, "104", "scam_confidence")
        __process_category(categories, result, "105", "potentially_illegal_confidence")
        __process_category(categories, result, "201", "misleading_claims_unethical_confidence")
        __process_category(categories, result, "202", "privacy_risks_confidence")
        __process_category(categories, result, "203", "suspicious_confidence")
        __process_category(categories, result, "204", "discrimination_confidence")
        __process_category(categories, result, "205", "spam_confidence")
        __process_category(categories, result, "206", "unwanted_programs_confidence")
        __process_category(categories, result, "207", "ads_popups_confidence")
    return result
def __process_category(categories, result, code, name):
    if code in categories:
        result[name] = categories[code]
def __process_value(value):
    if value < 20: return "[color=#ff0000]Very poor"
    elif value < 40: return "[color=#ff5631]Poor"
    elif value < 60: return "[color=#ffd500]Unsatisfactory"
    elif value < 80: return "[color=#a2e214]Good"
    elif value <= 100: return "[color=#60c100]Excellent"
    else: return "[color=grey]Out of range!"

class Linkinfo(ts3plugin):
    name = "Linkinfo"
    version = "2.0"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 21
    author = "Bluscream, Luemmel"
    description = "Prints a Linkinfolink to the chat."
    requestAutoload = True
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    hotkeys = []
    menuItems = []
    wot_api_key = ""
    bbcode_url = compile(r'\[url(?:|=[\'"]?([^]"\']+)[\'"]?]([^[]+)|](([^[]+)))\[\/url]', IGNORECASE)
    messages = []
    returnCode = ""

    def __init__(self):
        if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))

    def stop(self): pass

    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        if ffIgnored: return
        (error, myid) = ts3lib.getClientID(schid)
        _message = message.lower()
        if myid == fromID and not "~check~" in _message: return
        if not any(substring in _message for substring in ["[url]", "[url="]): return
        msg = {
            "schid": schid,
            "returnCode": ts3lib.createReturnCode(),
            "invoker": fromID,
            "targetMode": targetMode,
            "urls": parseURLs(message, self.bbcode_url),
            "response": "[b]Link Checker:[/b]"
        }
        hosts = []
        for url in msg["urls"]:
            if url[0] != url[1]:
                msg["response"] += "\n[color=orange]Suspicous Link [url]{}[/url] points to [url]{}[/url][/color]".format(url[0],url[1])
                # answerMessage(schid, targetMode, fromID, "[color=orange]{}: {}".format(url[0], url[1]))
            host = QUrl(url[1]).host()
            if host and "." in host and not host in hosts:
                hosts.append(host)
        if len(hosts) > 0:
            self.messages.append(msg)
            self.getLinkInfo(hosts)

    def getLinkInfo(self, urls):
        domains = "/".join(urls)
        url = "http://api.mywot.com/0.4/public_link_json2?hosts=%s/&key=%s" % (domains,self.wot_api_key)
        ts3lib.logMessage('Requesting %s'%url, ts3defines.LogLevel.LogLevel_ERROR, "PyTSon Linkinfo Script", 0)
        self.nwm = QNetworkAccessManager()
        self.nwm.connect("finished(QNetworkReply*)", self.onWOTReply)
        self.nwm.get(QNetworkRequest(QUrl(url)))

    def onWOTReply(self, reply):
        if reply.error() != QNetworkReply.NoError: print(reply.error())
        response = loads(str(reply.readAll().data().decode('utf-8')))
        _response = ""
        for domain in response:
            parsed = parse_attributes_for_report(response[domain])
            _response += "\n{}: {}".format(domain, parsed)
        # response = "\n" + dumps(response) # , indent=4, sort_keys=True)
        msg = self.messages[0]
        msg["response"] += _response
        answerMessage(msg["schid"], msg["targetMode"], msg["invoker"], msg["response"], msg["returnCode"])

    def onServerErrorEvent(self, schid, errorMessage, error, returnCode, extraMessage):
        return self.onServerPermissionErrorEvent(schid, errorMessage, error, returnCode, 0)
    def onServerPermissionErrorEvent(self, schid, errorMessage, error, returnCode, failedPermissionID):
        # (err, permid) = ts3lib.getPermissionIDByName(schid, "")
        for msg in self.messages:
            if returnCode == msg["returnCode"]:
                if error == ts3defines.ERROR_permissions_client_insufficient:
                    if msg["response"]: ts3lib.printMessageToCurrentTab(msg["response"])
                del msg
                return True
        return False