from socket import *


PORT = 9000
MAXLISTEN = 15
#--------------------------------------------------------------
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", PORT))
serverSocket.listen(MAXLISTEN)
while True:
    print ("server listening")
    newSocket, address = serverSocket.accept()
    print ("recieved connection from",address)
    newSocket.send("hello")
    newSocket.close()
