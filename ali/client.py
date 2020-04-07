from socket import *


MAXLISTEN = 15
SERVERPORT = 9000
MAXMSGLEN = 1000



#--------------------------------------------------------------
PORT = int(input("Enter port number:"))
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.bind(("", PORT))
clientSocket.connect(("",SERVERPORT))
data = clientSocket.recv(MAXMSGLEN)
for i in data:
    print(int(i))