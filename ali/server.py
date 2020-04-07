import time
from socket import *
import sys
import threading

PORT = 9000
MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000
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

def handle_client(msgSocket):
    print("inside new thread!")
    inputBuffer = ""
    msgSocket.sendall("Welcome to your FTP server! \nEnter USERNAME:" + EOF)
    print("data sent!")
    newMsg, inputBuffer = recvNextMsg(msgSocket, inputBuffer)
    print("data recieved ?")
    msgSocket.sendall("NEW" + newMsg + "NEW" + EOF)
    msgSocket.close()

#--------------------------------------------------------------
#--------------------------------------------------------------

def on_press(key):
    print (key)

#--------------------------------------------------------------
#--------------------------------------------------------------

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(("", PORT))
serverSocket.listen(MAXLISTEN)
while True:
    try:
        print ("server listening")
        msgSocket, address = serverSocket.accept()
        print ("creating new connection")
        t = threading.Thread(target = handle_client, args = (msgSocket,))
        t.setDaemon(True)
        t.start()
        print ("recieved connection from",address)
    except KeyboardInterrupt:
        if serverSocket:
            print("got Keyboard interrupt in main Program!")
            serverSocket.close()
            sys.exit()

