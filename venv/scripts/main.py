# Imports
import os
from tkinter import *
from tkinter.ttk import *
from winreg import *
from re import search
import json

# Variables
window = None
curOutput = None
curOutputText = ""
path_icon = ''
registry_hklm = None
registry_hkcu = None

# Path Replaces
pathReplaces = [
    {
        'toReplace': '%WIN%',
        'replaceWith': os.environ['WINDIR']
    },
    {
        'toReplace': '%TEMP%',
        'replaceWith': os.environ['TEMP']
    },
    {
        'toReplace': '%APPDATA%',
        'replaceWith': os.environ['APPDATA']
    }
]

# Start Function
def start():
    window = Tk()

    window.title('NoGov')
    window.iconbitmap('../imgs/NoGov2.ico')
    window.geometry("500x500")
    window.resizable(0, 0)

    style = Style()
    style.configure('Title.TLabel', font=('calibri', 15, 'bold'), borderwidth='4', foreground="black")
    style.configure('TLabel', font=('calibri', 10), borderwidth='4', foreground="black", justify='center')
    style.configure('TButton', font=('calibri', 10, 'bold'), foreground="green")

    label_1 = Label(window, text="NoGov 1.0.0", style="Title.TLabel")
    label_1.pack()

    button_check = Button(window, text="Check", command=startCheck)
    button_check.pack()

    global curOutput, curOutputText
    curOutputText = ""
    curOutput = Label(window, text=curOutputText)

    window.mainloop()

def startCheck():
    clearOutput()

    trojan_files = [pos_json for pos_json in os.listdir('../data/trojans/') if pos_json.endswith('.json')]

    for curTrojanFile in trojan_files:
        debug_log(-1, '---------------------------')
        debug_log(0, 'Loading trojan data from file: \"' + str(curTrojanFile)+"\"")
        curTrojanData = getTrojanJSONData(str(curTrojanFile))

        curTrojanState = str(checkSpecificSpyware(curTrojanData))
        addToOutput(curTrojanData['detail_name'] + ': \n' + curTrojanState + "\n")

def clearOutput():
    global curOutputText
    curOutputText = ""
    curOutput.config(text=curOutputText)
    curOutput.pack()

def addToOutput(string):
    global curOutputText
    curOutputText = curOutputText + string
    curOutput.config(text=curOutputText)
    curOutput.pack()

def getTrojanJSONData(filename):
    trojanFileRAWData = None
    with open('../data/trojans/' + filename) as curFile:
        trojanFileRAWData = curFile.read()
    return json.loads(trojanFileRAWData)

def convertPath(pathString):
    for item in pathReplaces:
        if search(item['toReplace'], str(pathString)):
            # PathString contains a value that needs to be replaced
            pathString = pathString.replace(item['toReplace'], item['replaceWith'])
    return pathString

def getOpenRegKey(hk, key):
    out = None
    if hk == "HKLM":
        out = OpenKey(registry_hklm, str(key))
    if hk == "HKCU":
        out = OpenKey(registry_hkcu, str(key))
    return out

def getProbabilityText(probabilityLevel):
    out = ""
    probabilityLevel = int(probabilityLevel)
    if probabilityLevel == 1:
        out = "Definitely"
    if probabilityLevel == 2:
        out = "Very likely"
    if probabilityLevel == 3:
        out = "Likely"
    if probabilityLevel == 4:
        out = "Evenutally"
    if probabilityLevel == 5:
        out = "Unreliable"

    return out

def checkSpecificSpyware(trojanData):
    debug_log(5, "Checking for trojan: \"" + trojanData['name'] + "\"")

    global registry_hklm, registry_hkcu
    registry_hklm = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    registry_hkcu = ConnectRegistry(None, HKEY_CURRENT_USER)

    out = False

    suffix = ''

    # Symptom Check: File exists
    for curPath in trojanData['symptoms']['fileExists']:
        # Convert Path
        curPath = convertPath(curPath)

        debug_log(5, 'Searching for: \"' + curPath + '\"')
        if os.path.isfile(curPath):
            # File found
            out = True
            suffix = '\nAlias: ' + trojanData['alias'] + "\n" + "Probability: " + getProbabilityText(trojanData['probabilityLevel'])

            debug_log(6, 'Suspicous file found: \"' + str(curPath) + '\"')
        else:
            # File not found
            debug_log(6, 'Suspicous file not found: \"' + str(curPath) + '\"')
            break

    # Symptom Check: Registry Value contains
    for curRegistryKey in trojanData['symptoms']['registryKeyValue']:
        try:
            parentKey = getOpenRegKey(str(curRegistryKey[0]), str(curRegistryKey[1]))
            keyValue = QueryValueEx(parentKey, curRegistryKey[2])

            if search(curRegistryKey[3], str(keyValue)):
                # Regkey value does contain
                out = True
                suffix = '\nAlias: ' + trojanData['alias'] + "\n" + "Probability: " + getProbabilityText(trojanData['probabilityLevel'])

                debug_log(6, 'Regkey: \"' + str(curRegistryKey[0]) + '\\' + str(curRegistryKey[1]) + "\\" + str(curRegistryKey[2]) + '\"' + ' does contain suspicious value: \"' + curRegistryKey[3] + '\"')
            else:
                # Regkey value does not contain
                debug_log(6, 'Regkey: \"' + str(curRegistryKey[0]) + '\\' + str(curRegistryKey[1]) + "\\" + str(curRegistryKey[2]) + '\"' + ' does not contain suspicious value: \"' + curRegistryKey[3] + '\"')
                break
        except:
            pass
            # Regkey doesn't exist
            debug_log(6, 'Regkey not found: \"' + str(curRegistryKey[0]) + '\\' + str(curRegistryKey[1]) + "\\" + str(curRegistryKey[2]) + '\"')

    # Beautify output
    if out:
        out = 'Was found' + suffix + "\n"
        debug_log(7, trojanData['name'] + " was found")
    else:
        out = 'Not found' + suffix + "\n"
        debug_log(7, trojanData['name'] + " was not found")

    return out

def debug_log(type, value):
    prefix = ''
    if type == 0:
        prefix = '[INFO] '
    if type == 1:
        prefix = '[WARNING] '
    if type == 2:
        prefix = '[ERROR] '
    if type == 3:
        prefix = '[CRITITCAL] '
    if type == 5:
        prefix = '[CHECK] '
    if type == 6:
        prefix = '[SYMPTOMRESULT] '
    if type == 7:
        prefix = '[RESULT] '
    print(prefix + value)

# Init
start()