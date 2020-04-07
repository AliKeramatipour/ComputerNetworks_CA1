import time
from socket import *
import threading

SERVERPORT = 9000
MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000
#--------------------------------------------------------------

def recvNextMsg(msgSocket, inputBuffer):
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
            msgSocket.sendall("QUIT" + EOF)
            msgSocket.close()
        sys.exit()
    
#--------------------------------------------------------------
#--------------------------------------------------------------

PORT = int(input("Enter port number:"))
msgSocket = socket(AF_INET, SOCK_STREAM)
msgSocket.bind(("", PORT))
msgSocket.connect(("",SERVERPORT))
inputBuffer = ""

print("here?")
data, inputBuffer = recvNextMsg(msgSocket, inputBuffer)
print(data)
print("stuck here?")
msgSocket.sendall("hello n welcome why are u gey" + EOF)
data, inputBuffer = recvNextMsg(msgSocket, inputBuffer)
print("nah not stuck")
print(data)
for i in data:
    print(ord(i))
msgSocket.close()