import pickle
import random
import socket
import struct
import sys

sys.path.append('../shared')


import time
from threading import Timer
from state_updater import StateUpdater
import server_to_client


SERVER_ADDRESS = ('localhost', 6666)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

last_received_seq_nr = 0

sock.sendto(b'init', SERVER_ADDRESS)
data, address = sock.recvfrom(1024)
my_state = server_to_client.deserialize(data)

players = []

state_updater = StateUpdater(
    sock=sock, updates_per_second=60, state=my_state, server_address=SERVER_ADDRESS)

while True:
    data, address = sock.recvfrom(1024)
    unpacked = pickle.loads(data)

    seq_nr = unpacked[0]
    if (seq_nr < last_received_seq_nr):
        continue

    unpacked_players = [server_to_client.deserialize(
        unpacked[i]) for i in range(1, len(unpacked))]

    print(unpacked_players)
