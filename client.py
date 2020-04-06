import socket
import os
import shutil

SERVER = "127.0.0.1"
PORT = 8080

enteredPass = False
user = ''
currentDirectory = ''
loggedIn = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("This is from Client",'UTF-8'))
while True:
    in_data =  client.recv(1024)
    msg = in_data.decode()
    splitted = msg.split()
    if(msg == '331 User name okay, need password.'):
        enteredPass = True
    if(msg == '430 Invalid usename or password'):
        user = ''
    if(msg == '230 User logged in, proceed.'):
        currentDirectory = os.getcwd()
        loggedIn = True
    if(msg == 'PWD'):
        if loggedIn:
            msg = '257 ' + currentDirectory
        else:
            msg = '332 Need account for login.'
    if(splitted[0] == 'MKD'):
        if loggedIn:
            if splitted[1] == '-i':
                path = currentDirectory + '/' + splitted[2]
                if not os.path.exists(path):
                    os.makedirs(path)
                    msg = '257 ' + splitted[2] + ' created.'
                else:
                    msg = '500 Error.'
            else:
                path = splitted[1]
                if not os.path.exists(path):
                    os.makedirs(path)
                    msg = '257 ' + splitted[1] + ' created.'
                else:
                    msg = '500 Error.'
        else:
            msg = '332 Need account for login.'
    if(splitted[0] == 'RMD'):# ?
        if loggedIn:
            if splitted[1] == '-f':
                path = currentDirectory + '/' + splitted[2]
                if os.path.exists(path):
                    # os.remove(path)
                    shutil.rmtree(path)
                    msg = '250 ' + splitted[2] + ' deleted.'
                else:
                    msg = '500 Error.'
            else:
                path = splitted[1]
                if os.path.exists(path):
                    shutil.rmtree(path)
                    # os.remove(path)
                    msg = '250 ' + path + ' deleted.'
                else:
                    msg = '500 Error.'
        else:
            msg = '332 Need account for login.'
    if(splitted[0] == 'CWD'):
        if loggedIn:
            path = splitted[1]
            if os.path.exists(path):
                os.chdir(path)
                currentDirectory = os.getcwd()
                msg = '250 Succesful Change.'
        else:
            msg = '332 Need account for login.'


    print("From Server :" ,msg)
    out_data = input()
    splitted = out_data.split()
    if splitted[0] == 'USER':
        user = splitted[1]
    if (enteredPass and splitted[0] == 'PASS'):
        enteredPass = False
        out_data = '*T ' + user + ' ' + splitted[1]
    if (enteredPass and splitted[0] != 'PASS'):
        enteredPass = False
        user = ''
        out_data = "*F " + out_data
    client.sendall(bytes(out_data,'UTF-8'))
    if out_data=='bye':
        break
client.close()