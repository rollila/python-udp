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
import shared_utils


SERVER_ADDRESS = ('localhost', 6666)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

last_received_seq_nr = 0

sock.sendto(b'init', SERVER_ADDRESS)
data, address = sock.recvfrom(1024)
my_state = server_to_client.deserialize(data)

players = []

state_updater = StateUpdater(
    sock=sock, updates_per_second=60, state=my_state, server_address=SERVER_ADDRESS)


def print_update():
    print('\033[H\033[J')
    print('My location: {}'.format(my_state['location']))

    if (len(players) > 0):
        print('I can see the following other players:')
        for player in players:
            print('Id: {}, distance from me: {}'.format(
                player['id'], shared_utils.distance(my_state['location'], player['location'])))


while True:
    data, address = sock.recvfrom(60000)
    if (data == b'not_recognized'):
        raise RuntimeError('Disconnected from server')

    unpacked = pickle.loads(data)

    seq_nr = unpacked[0]
    if (seq_nr < last_received_seq_nr):
        continue

    players = [server_to_client.deserialize(
        unpacked[i]) for i in range(1, len(unpacked))]

    print_update()
