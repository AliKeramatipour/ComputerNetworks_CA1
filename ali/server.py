import time
from socket import *
import sys
import threading
import json
import os
import shutil

MSGPORT  = 9000
FILEPORT = 9001
MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000
DEFAULTDIR = "./dir"
MINDIRLEN = 2

#--------------------------------------------------------------

commands = ['USER','PASS','PWD','MKD','RMD','LIST','CWD','DL','HELP','QUIT']
user = []
password = []
size = []
email = []
alert = []
admin = []
commandChannelPort = 0
dataChannelPort = 0
accountingEnable = False
accountingThreshold = 0
loggingEnable = False
loggingPath = ""
authorizationEnable = False
authorizationFiles = []

def preprocessUsers():
    file = open ('config.json', "r") 
    config = json.loads(file.read())
    for i in config['users']: 
        user.append(i['user']) 
        password.append(i['password'])
    for i in config['accounting']['users']:
        size.append(i['size'])
        email.append(i['email'])
        alert.append(i['alert'])
    for i in config['authorization']['admins']:
        for j in user:
            if j == i:
                admin.append(1)
            else:
                admin.append(0)
    commandChannelPort = config['commandChannelPort']
    dataChannelPort = config['dataChannelPort']
    accountingEnable = config['accounting']['enable']
    accountingThreshold = config['accounting']['threshold']
    loggingEnable = config['logging']['enable']
    loggingPath = config['logging']['path']
    authorizationEnable = config['authorization']['enable']

    for i in config['authorization']['files']:
        authorizationFiles.append(i)
    file.close() 
    return

#--------------------------------------------------------------
#--------------------------------------------------------------

def recvNextMsg(msgSocket, inputBuffer):
    data = ""
    while True:
        inputBuffer = inputBuffer + data
        data = msgSocket.recv(MAXMSGLEN)
        for c in data:
            if c == EOF:
                left, right = data.split(EOF,1)
                msg = inputBuffer + left
                inputBuffer = right
                return msg, inputBuffer

#--------------------------------------------------------------
#--------------------------------------------------------------

def handle_client(msgSocket, fileSocket, address):
    print("-created new thread for user at " + str(address[0]) + ' ' + str(address[1]))

    inputBuffer = ""
    loggedIn = False
    currentDirectory = DEFAULTDIR
    currentUsername = ""
    userID = 0

    sendMsg(msgSocket, "Connection established. \nenter HELP for command list:" )
    while True:
        instruction, inputBuffer = recvNextMsg(msgSocket, inputBuffer)
        print("--instruction recieved: " + instruction)
        instruction = instruction + " "
        data, inputs = instruction.split(" ",1)

        if not (data in commands):
            sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
            continue
        if data == "HELP":
            HELP(inputs, msgSocket)
            continue
        elif data == "QUIT":
            sendMsg(msgSocket, "221 Successful Quit.")
            break
        elif data == "USER":
            if loggedIn == True:
                sendMsg(msgSocket, "500 Already logged in.")
                continue
            currentUsername = USER(inputs, msgSocket)
            continue
        elif data == "PASS":
            if loggedIn == True:
                sendMsg(msgSocket, "500 Already logged in.")
                continue
            userID = PASS(inputs, currentUsername, msgSocket)
            if userID == -1:
                currentUsername = ""
            else:
                loggedIn = True
            continue
        elif loggedIn == False:
            sendMsg(msgSocket, "332 Need account for login.")
            continue
        else:
            if data == "LIST":
                LIST(currentDirectory, inputs, msgSocket, fileSocket)
                continue
            elif data == "PWD":
                PWD(inputs, currentDirectory, msgSocket)
                continue
            elif data == "MKD":
                MKD(inputs, currentDirectory, msgSocket)
                continue
            elif data == "RMD":
                RMD(inputs, currentDirectory, msgSocket, userID)
                continue
            elif data == "CWD":
                CWD(inputs, currentDirectory, msgSocket)
                continue
            elif data == "DL":
                DL(inputs, currentDirectory, msgSocket, fileSocket, userID)
                if size[userID] < accountingThreshold:
                    sendEmail(userID)
                continue
        

    msgSocket.close()
    fileSocket.close()

#--------------------------------------------------------------
#--------------------------------------------------------------

def sendEmail(userID):
    #sendEmail
    return

#--------------------------------------------------------------
#--------------------------------------------------------------

def HELP(inputs, msgSocket):
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return

    file = open("etc/help.txt","r") 
    sendMsg(msgSocket, file.read())

#--------------------------------------------------------------
#--------------------------------------------------------------

def QUIT(inputs, msgSocket):
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return
    
    print("--user quiting")
    sendMsg(msgSocket, "221 Successful Quit.")

#--------------------------------------------------------------
#--------------------------------------------------------------

def USER(inputs, msgSocket):
    if len(inputs) == 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return ""

    data, inputs = inputs.split(" ",1)
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return ""
    sendMsg(msgSocket, "331 User name okay, need password.")
    return data

#--------------------------------------------------------------
#--------------------------------------------------------------

def PASS(inputs, currentUsername, msgSocket):
    data, inputs = inputs.split(" ",1)

    if len(currentUsername) == 0:
        sendMsg(msgSocket, "503 Bad sequence of commands.")
        return -1
    
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return -1
    
    for i in range(0, len(user)):
        if user[i] == currentUsername:
            sendMsg(msgSocket, "230 User logged in, proceed.")
            return i

    sendMsg(msgSocket, "430 Invalid username or password.")
    return -1

#--------------------------------------------------------------
#--------------------------------------------------------------

def LIST(currentDirectory, inputs, msgSocket, fileSocket):
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return

    listOfFiles = ""
    for file in os.listdir(currentDirectory):
        if file[0] != '.' and '.ini' not in file and '.BIN' not in file :
            listOfFiles += file + '\n'
    listOfFiles = listOfFiles[:-1]
    sendMsg(msgSocket, "226 List transfer done.")
    sendMsg(fileSocket, listOfFiles)

#--------------------------------------------------------------
#--------------------------------------------------------------

def PWD(inputs, currentDirectory, msgSocket):
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return
    sendMsg(msgSocket, "257 " + currentDirectory)

#--------------------------------------------------------------
#--------------------------------------------------------------

def CWD(inputs, currentDirectory, msgSocket):
    if len(inputs) == 0:
        currentDirectory = DEFAULTDIR
        sendMsg(msgSocket, "250 Successful Change.")
        return currentDirectory
    
    data, inputs = inputs.split(" ",1)
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return currentDirectory
    
    currentDirectoryList = currentDirectory.split("/")
    directoryList = data.split("/")
    for folder in directoryList:
        if folder == '..':
            if len(currentDirectoryList) <= MINDIRLEN:
                sendMsg(msgSocket, "500 Not a valid directory.")
                return currentDirectory
            else:
                currentDirectoryList.pop()
                continue
        elif folder == '.':
            continue
        if '.' in folder:
            sendMsg(msgSocket, "500 Not a valid directory.")
            return currentDirectory
        
        currentDirectoryList.append(folder)
        tempDir = '/'.join(currentDirectoryList)
        if not os.path.exists(tempDir):
            sendMsg(msgSocket, "500 Not a valid directory.")
            return currentDirectory
    
    sendMsg(msgSocket, "250 Successful Change.")
    return '/'.join(currentDirectoryList)

#--------------------------------------------------------------
#--------------------------------------------------------------

def MKD(inputs, currentDirectory, msgSocket):
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return
    
    flag, createDir = inputs.split(" ",1)
    if len(createDir) != 0:
        if flag != "-i":
            sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
            return
        if '/' in createDir or createDir == '.' or createDir == '..':
            sendMsg(msgSocket, "500 Cannot have '/' in filename or '.' or '..' as filename")
            return
        if os.path.exists(currentDirectory + "/" + createDir):
            sendMsg(msgSocket, "500 File already exists")
            return
        open(currentDirectory + "/" + createDir, 'w')
        sendMsg(msgSocket, "257 " + createDir + " created.")
        return
    
    createDir = flag
    if '/' in createDir or createDir == '.' or createDir == '..':
        sendMsg(msgSocket, "500 Cannot have '/' in filename or '.' or '..' as filename")
        return
    if os.path.exists(currentDirectory + "/" + createDir):
        sendMsg(msgSocket, "500 Folder already exists")
        return
    os.makedirs(currentDirectory + "/" + createDir)
    sendMsg(msgSocket, "257 " + createDir + " created.")

#--------------------------------------------------------------
#--------------------------------------------------------------

def RMD(inputs, currentDirectory, msgSocket, userID):
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return
    
    flag, removeDir = inputs.split(" ",1)
    if len(removeDir) != 0:
        tmpDir = removeDir
        removeDir = currentDirectory + "/" + removeDir
        if flag != "-f":
            sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
            return
        if not os.path.exists(removeDir):
            sendMsg(msgSocket, "510 Folder does not exist.")
            return
        shutil.rmtree(removeDir)
        sendMsg(msgSocket, "250 " + tmpDir + " deleted.")
        return
    
    removeDir = flag
    tmpDir = removeDir
    removeDir = currentDirectory + "/" + removeDir

    if (not os.path.exists(removeDir)) or (removeDir in authorizationFiles and admin[userID] == False):
        sendMsg(msgSocket, "550 File unavailable.")
        return
    os.remove(removeDir)
    sendMsg(msgSocket, "250 " + tmpDir + " deleted.")

#--------------------------------------------------------------
#--------------------------------------------------------------

def DL(inputs, currentDirectory, msgSocket, fileSocket, userID):
    if len(inputs) == 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return
    
    filename, inputs = inputs.split(" ",1)
    if len(inputs) != 0:
        sendMsg(msgSocket, "501 Syntax error in parameters or arguments.")
        return
    downloadDir = currentDirectory + "/" + filename
    if (not os.path.exists(downloadDir) or (downloadDir in authorizationFiles and admin[userID] == False)):
        sendMsg(msgSocket, "550 File unavailable.")
        return

    f = open(downloadDir, "rb")
    data = f.read()
    if data > size[userID] and accountingEnable:
        sendMsg(fileSocket, "file can not be transimitted.")
        sendMsg(msgSocket, "425 Can't open data connection.")
        return
    sendMsg(fileSocket, data)
    sendMsg(msgSocket, "226 Successful Download.")
    size[userID] -= len(data)
    return

#--------------------------------------------------------------
#--------------------------------------------------------------

def on_press(key):
    print (key)

#--------------------------------------------------------------
#--------------------------------------------------------------

def sendMsg(msgSocket, message):
    msgSocket.sendall(message + EOF)

#--------------------------------------------------------------
#--------------------------------------------------------------

preprocessUsers()
msgListenSocket = socket(AF_INET, SOCK_STREAM)
msgListenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
msgListenSocket.bind(("", MSGPORT))
msgListenSocket.listen(MAXLISTEN)

fileListenSocket = socket(AF_INET, SOCK_STREAM)
fileListenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
fileListenSocket.bind(("", FILEPORT))
fileListenSocket.listen(MAXLISTEN)

while True:
    try:
        print ("server listening")
        msgSocket, address = msgListenSocket.accept()
        #need to set a timeout later
        fileSocket, address = fileListenSocket.accept()
        print ("creating new connection")
        t = threading.Thread(target = handle_client, args = (msgSocket, fileSocket, address))
        t.setDaemon(True)
        t.start()
        print ("recieved connection from",address)
    except KeyboardInterrupt:
        print("got Keyboard interrupt in main Program!")
        msgListenSocket.close()
        fileListenSocket.close()
        sys.exit()

