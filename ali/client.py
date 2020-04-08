import time
from socket import *
import threading

MSGPORT  = 9000
FILEPORT = 9001
MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000
#--------------------------------------------------------------

def recvNextMsg(inputBuffer):
    data = left = right = ""
    try:
        while True:
            inputBuffer = inputBuffer + data
            data = msgSocket.recv(MAXMSGLEN)
            for c in data:
                if c == EOF:
                    left,right = data.split(EOF,1)
                    msg = inputBuffer + left
                    inputBuffer = right
                    return msg, inputBuffer
    except KeyboardInterrupt:
        if msgSocket:
            sendMsg("QUIT")
            msgSocket.close()
        sys.exit()
    
#--------------------------------------------------------------
#--------------------------------------------------------------

def sendMsg(message):
    msgSocket.sendall(message + EOF)
    return

#--------------------------------------------------------------
#--------------------------------------------------------------

PORT = int(input("Enter port number:"))
global msgSocket
global fileSocket
msgSocket = socket(AF_INET, SOCK_STREAM)
msgSocket.bind(("", PORT))
msgSocket.connect(("", MSGPORT))

fileSocket = socket(AF_INET, SOCK_STREAM)
fileSocket.bind(("", PORT))
fileSocket.connect(("", FILEPORT))


inputBuffer = ""
data, inputBuffer = recvNextMsg(msgSocket, inputBuffer)
msgSocket.close()