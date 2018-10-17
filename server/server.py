import pickle
import socket
import sys

sys.path.append('../shared')

import time
from threading import Timer
from player_state import PlayerState
from player_controller import PlayerController
from state_broadcaster import StateBroadcaster
import server_to_client
import client_to_server

MAX_PLAYERS = 10
MAX_KBITS_PER_SEC = 75
TARGET_OBJECT_NUMBER = 5
MAX_BYTES_PER_SEC = MAX_KBITS_PER_SEC * 1000 / 8


def handle(data, address):
    if (data == b'init'):
        if (len(players.players) >= MAX_PLAYERS):
            sock.sendto(b'server_full', address)
        else:
            new_player = players.add_player(address, (100, 100))
            message = server_to_client.serialize(
                new_player.id, new_player.location)

            sock.sendto(message, address)

    else:
        unpacked = client_to_server.deserialize(data)

        if players.has_player_with_address(address):
            players.update_player_state(
                unpacked['id'], unpacked['location'], unpacked['seq_nr'])
        else:
            sock.sendto(b'not_recognized', address)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 6666)
print('Server starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

players = PlayerController()
state_broadcaster = StateBroadcaster(
    players.players, sock, MAX_BYTES_PER_SEC, TARGET_OBJECT_NUMBER)


while True:
    received, address = sock.recvfrom(1024)
    handle(received, address)
