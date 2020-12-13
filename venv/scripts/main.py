# Imports
import os
from tkinter import *
from tkinter.ttk import *
from winreg import *
from re import search

# Variables
window = None
curOutput = None
curOutputText = ""
path_icon = ''

# Spyware - Intern Name
spyware_names = [
    # Finfisher Finspy
    'finspy',
    # Blackshades
    'blackshades'
]

# Spyware - Detail Name
spyware_detail_names = [
    # Finfisher Finspy
    'Finfisher Finspy',
    # Blackshades
    'Blackshades'
]

# Spyware - Detail Suffix
spyware_detail_suffix = [
    # Finfisher Finspy
    'Backdoor:Win32/R2d2.A',
    # Blackshades
    'Worm:Win32/Cambot.A'
]

# Spyware - Look up as many files (Does Exist search)
spyware_exist_paths = [
    # Finfisher Finspy
    [
        os.environ['WINDIR'] + '\System32\mfc42ul.dll',
        os.environ['WINDIR'] + '\System32\winsys32.sys'
    ],
    # Blackshades
    [
        os.environ['TEMP'] + '\goolge.exe.jpg',
        os.environ['APPDATA'] + '\goolge.exe'
    ]
]

# Spyware - Registry Checks
# First: Path
# Second: Key
# Value to search for (Regex Search)
spyware_registry_key = [
    # Finfisher Finspy
    [
        [
            'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows',
            'AppInit_DLLs',
            'mfc42ul.dll'
        ]
    ],
    # Blackshades
    [
        [
            'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
            'Google Tools',
            'goolge.exe'
        ],
        [
            'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run',
            'Google Tools',
            'goolge.exe'
        ]
    ]
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
    style.configure('TLabel', font=('calibri', 10), borderwidth='4', foreground="black")
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

    i = 0
    for curName in spyware_names:
        addToOutput(spyware_detail_names[i] + ': ' + str(checkSpecificSpyware(curName)) + "\n")
        i = i + 1

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

def checkSpecificSpyware(type):
    debug_log(0, "Checking for: " + type)
    registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    out = False

    foundSuffix = ''

    curIndex = spyware_names.index(type)

    for curPath in spyware_exist_paths[curIndex]:
        if os.path.isfile(curPath):
            out = True
            foundSuffix = ' - ' + spyware_detail_suffix[curIndex]
            break
        for curRegistryKey in spyware_registry_key[curIndex]:
            try:
                parentKey = OpenKey(registry, str(curRegistryKey[0]))
                keyValue = QueryValueEx(parentKey, curRegistryKey[1])
                if search(curRegistryKey[2], str(keyValue)):
                    out = True
                    foundSuffix = ' - ' + spyware_detail_suffix[curIndex]
                    break
            except:
                debug_log(0, "Regkey not found. Value: " + str(curRegistryKey[0]) + "\\" + str(curRegistryKey[1]))

    # Beautify output
    if out:
        out = 'Was found' + foundSuffix
    else:
        out = 'Not found'

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
    print(prefix + value)

# Init
start()