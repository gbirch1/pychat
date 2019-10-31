#!/usr/bin/env python3.7

# imports
import select, socket, sys # routing
from pychat_util import Room, Hall, Player # config classes
import pychat_util # config file

# max message size
READ_BUFFER = 4096

# handle error of no ip on startup
if len(sys.argv) < 2: # sys.argv is user input while starting the program
    print("Usage: Python3 client.py [hostname]", file = sys.stderr)
    sys.exit(1) # handle error exit app
else:
    # sever connetion
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INEt = ipv4 SOCK_STREAM = tcp protocall 
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # SOL_SOCKET = define protocol level SO_REUSEADDR = reuse socket
    server_connection.connect((sys.argv[1], pychat_util.PORT)) # connection established 

# display in terminal
def prompt():
    print('>', end=' ', flush = True)

# dissplay from server connection
print("Connected to server\n")
msg_prefix = ''

socket_list = [sys.stdin, server_connection]

# main loop
while True:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for s in read_sockets:
        if s is server_connection: # incoming message
            msg = s.recv(READ_BUFFER)
            if not msg:
                print("Server down!") # server crash
                sys.exit(2)
            else: # quit
                if msg == pychat_util.QUIT_STRING.encode():
                    sys.stdout.write('Bye\n')
                    sys.exit(2)
                else: # set name
                    sys.stdout.write(msg.decode())
                    if 'Please tell us your name' in msg.decode():
                        msg_prefix = 'name: ' # identifier for name
                    else: # wait for message
                        msg_prefix = ''
                    prompt() # dissplay prompt after every message

        else: # send data and handle encryption
            alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890<>' # do not change
            key = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_5647382910<>' # change only if directed to need to be the same for every client
            alphabet_key = dict(zip(alphabet, key)) # zip to dict for encryption
            msg = msg_prefix + sys.stdin.readline() # define message 
            # encode
            if "<encode>" in msg:
                string = msg[8:] # cut prefix
                ciphertext = '' # convertion
                for char in string:
                    for key in alphabet_key:
                        if key in char:
                            char = alphabet_key[key]
                            ciphertext = ciphertext + char
                            break
                server_connection.sendall((ciphertext + '\n').encode()) #send
            # decode
            elif "<decode>" in msg:
                string = msg[8:] # cut prefix
                plaintext = '' # convertion
                for char in string:
                    for key, value in alphabet_key.items():
                        if value in char:
                            char = key
                            plaintext = plaintext + char
                            break
                print (plaintext + '\n') # print msg
                prompt()
            else:
                server_connection.sendall(msg.encode()) # send msg


