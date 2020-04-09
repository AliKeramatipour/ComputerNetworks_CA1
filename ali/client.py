import time
from socket import *
import threading
import sys
import os

MSGPORT  = 9000
FILEPORT = 9001
MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000
#--------------------------------------------------------------

def recvNextMsg(msgSocket, inputBuffer):
    data = ""
    while True:
        data = msgSocket.recv(MAXMSGLEN)
        inputBuffer = inputBuffer + data
        
        if len(inputBuffer) % 2 == 1:
            continue
        
        msg = ""
        for i in range(0, len(inputBuffer)):
            if i % 2 == 1:
                msg = msg + inputBuffer[i]
            else:
                if inputBuffer[i] == '1':
                    return msg, inputBuffer[i+2:]
                
#--------------------------------------------------------------
#--------------------------------------------------------------

def sendMsg(message):
    msgSocket.sendall(message + EOF)
    return

#--------------------------------------------------------------
#--------------------------------------------------------------

PORT = int(raw_input("Enter port number: "))
PATH = "clients/" + str(PORT)
if not os.path.exists(PATH):
    os.makedirs(str(PATH))
PATH += "/"

msgSocket = socket(AF_INET, SOCK_STREAM)
msgSocket.bind(("", PORT))
try :
    msgSocket.connect(("", MSGPORT))
except error:
    print("500 could not establish connection to server")
    msgSocket.close()
    sys.exit()

fileSocket = socket(AF_INET, SOCK_STREAM)
fileSocket.bind(("", PORT + 1))

try:
    fileSocket.connect(("", FILEPORT))
except error:
    print("500 could not establish connection to server")
    msgSocket.close()
    fileSocket.close()
    sys.exit()


data = inputBuffer = fileData = fileBuffer = ""
data, inputBuffer = recvNextMsg(msgSocket, inputBuffer) 
print(data)
while True:
    try:
        cmd = raw_input("your next command: ")
        sendMsg(cmd)
        data, inputBuffer = recvNextMsg(msgSocket, inputBuffer) 
        print(data)
        if data[0:3] == "332":
            continue
        if cmd == "QUIT":
            sys.exit()
        if cmd == "LIST":
            fileData, fileBuffer = recvNextMsg(fileSocket, fileBuffer)
            print (fileData)
        if ( cmd[0:2] == "DL" ):
            f = open(PATH + cmd,"w+")
            fileData, fileBuffer = recvNextMsg(fileSocket, fileBuffer)
            f.write(fileData)
            f.close()
    except:
        msgSocket.close()
        fileSocket.close()
        sys.exit()

