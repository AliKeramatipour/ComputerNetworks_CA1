import time
from socket import *
import sys
import threading
import json

MSGPORT  = 9000
FILEPORT = 9001
MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000

#--------------------------------------------------------------

def preprocessUsers():

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
    print("-created new thread for user at " + address)
    inputBuffer = ""
    loggedIn = False
    #username
    msgSocket.sendall("Welcome to your FTP server! \nEnter USERNAME:" + EOF)

    while True:
        instruction, inputBuffer = recvNextMsg(msgSocket, inputBuffer)
        



    msgSocket.close()

#--------------------------------------------------------------
#--------------------------------------------------------------

def on_press(key):
    print (key)

#--------------------------------------------------------------
#--------------------------------------------------------------

def sendMsg(key):
    print (key)

#--------------------------------------------------------------
#--------------------------------------------------------------

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

