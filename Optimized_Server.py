import socket
from _thread import *
from player import Player
import Network
import pickle
import sys
from events import *

server = "192.168.1.3"
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 5555
currentPlayer = 0

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    s.bind((host_ip,port))
except socket.error as e:
    str(e)


s.listen(2)
print("Waiting for a Connection")

players = [Player(0,0,50,50,(255,0,0)),Player(100,100,50,50,(0,0,255))]

connectionList = []

def threaded_Client(conn,currentPlayer):
    conn.send(pickle.dumps(Players(players,currentPlayer)))
    while True:
        try:
            data = pickle.loads(conn.recv(100))
            # print(data.action +str(data.playerNumber))
            if not data:
                print("diconnected")
                break
            else:
                for conns in connectionList:
                    conns.sendall(pickle.dumps(data))
        except:
            break
    print("Lost connection")
    conn.close()

while True:
    conn,addr = s.accept()
    connectionList.append(conn)
    print("Connected to:", addr)
    start_new_thread(threaded_Client, (conn, currentPlayer))
    currentPlayer += 1

