import socket
import threading
import json 
import os

# JSON file 
f = open ('config.json', "r") 
# Reading from file 
config = json.loads(f.read())
for i in config['users']: 
    print(i['user']) 

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)
    def run(self):
        print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode()
            splitted = msg.split()
            print ("from client", msg)
            if msg=='bye':
                break
            elif splitted[0] == 'USER':
                found = False
                for i in config['users']:
                    if i['user']==splitted[1]:
                        found = True
                        msg = '331 User name okay, need password.'
                if not found:
                    msg = '430 Invalid usename or password'
            elif splitted[0] == '*F':
                msg = '503 Bad sequence of commands.'
            elif splitted[0] == '*T':
                for i in config['users']:
                    if i['user']==splitted[1]:
                        if i['password']==splitted[2]:
                            msg = '230 User logged in, proceed.'
                        else:
                            msg = '430 Invalid usename or password'
            elif splitted[0] == 'PASS':
                msg = '503 Bad sequence of commands.'
            elif splitted[0] == 'PWD':
                msg = msg
            elif splitted[0] == 'MKD':
                msg = msg
            elif splitted[0] == 'RMD':
                msg = msg
            elif splitted[0] == 'CWD':
                msg = msg
            else:
                msg = '501 Syntax error in parameters or arguments.'
            self.csocket.send(bytes(msg,'UTF-8'))
        print ("Client at ", clientAddress , " disconnected...")

LOCALHOST = "127.0.0.1"
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("Server started")
print("Waiting for client request..")
while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
f.close() 