#!/usr/bin/env python3
import socket

host = "127.0.0.1"
port = 6600

reply = str.encode("You got me!")

server_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_sock.bind((host, port))

print(f"UDP server listening on {host}:{port}")

n=0
while(True):
    data = server_sock.recvfrom(1024)

    msg = data[0]
    address = data[1]

    if n % 10000 == 0:
        print("TOCK!", n, msg)
    n += 1

    #print(f"got {msg} from {address}")

    # Sending a reply to client only if they send the correct message!
    if msg == b'sekretsquirrel':    
        print(f"Got the secret message: {msg}")
        server_sock.sendto(reply, address)
