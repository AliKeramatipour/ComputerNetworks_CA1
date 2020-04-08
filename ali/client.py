import time
from socket import *
import threading
import sys

MSGPORT  = 9000
FILEPORT = 9001
MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000
#--------------------------------------------------------------

def recvNextMsg(inputBuffer):
    data = left = right = ""
    while True:
        inputBuffer = inputBuffer + data
        data = msgSocket.recv(MAXMSGLEN)
        for c in data:
            if c == EOF:
                left,right = data.split(EOF,1)
                msg = inputBuffer + left
                inputBuffer = right
                return msg, inputBuffer
    
#--------------------------------------------------------------
#--------------------------------------------------------------

def recvNextFile(fileBuffer):
    data = left = right = ""
    while True:
        fileBuffer = fileBuffer + data
        data = fileSocket.recv(MAXMSGLEN)
        for c in data:
            if c == EOF:
                left,right = data.split(EOF,1)
                msg = fileBuffer + left
                fileBuffer = right
                return msg, fileBuffer
    
#--------------------------------------------------------------
#--------------------------------------------------------------

def sendMsg(message):
    msgSocket.sendall(message + EOF)
    return

#--------------------------------------------------------------
#--------------------------------------------------------------

PORT = int(raw_input("Enter port number: "))
os.makedirs(str(PORT))
global msgSocket
global fileSocket
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
data, inputBuffer = recvNextMsg(inputBuffer) 
print(data)
while True:
    try:
        cmd = raw_input("your next command: ")
        sendMsg(cmd)
        if cmd == "QUIT":
            sys.exit()
        if cmd == "LIST":
            fileData, fileBuffer = recvNextFile(fileBuffer)
            print (fileData)
        if ( cmd[0:2] == "DL" ):
            f = open(cmd,"w+")
            fileData, fileBuffer = recvNextFile(fileBuffer)
            f.write(fileData)
        data, inputBuffer = recvNextMsg(inputBuffer) 
        print(data)
    except KeyboardInterrupt:
        msgSocket.close()
        fileSocket.close()
        sys.exit()

