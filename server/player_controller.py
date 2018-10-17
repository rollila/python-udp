import pickle
import time
from threading import Timer
from player_state import PlayerState
from client_state import ClientState


class PlayerController:

    def __init__(self):
        self.players = {}
        self.next_player_id = 0
        self.timer = Timer(20, self.prune_disconnected)
        self.timer.start()

    def add_player(self, address, location):
        self.next_player_id += 1
        new_player = PlayerState(location, self.next_player_id)
        client = ClientState(address, new_player)
        self.players[new_player.id] = client
        return new_player

    def update_player_state(self, player_id, location, seq_nr):
        if (self.players[player_id]):
            # Discard state updates received out of order
            if (self.players[player_id].last_received_seq < seq_nr):
                self.players[player_id].player_state.location = location
                self.players[player_id].last_received_seq = seq_nr
                self.players[player_id].last_received_timestamp = time.time()

    def prune_disconnected(self):
        todel = []
        for player_id in self.players:
            client = self.players[player_id]
            if (client.disconnected):
                todel.append(player_id)
            elif (client.last_received_timestamp < time.time() - 20):
                client.disconnected = True

        for player_id in todel:
            del self.players[player_id]

        self.timer = Timer(1, self.prune_disconnected)
        self.timer.start()

    def has_player_with_address(self, address):
        return any(self.players[player_id].address == address for player_id in self.players)
