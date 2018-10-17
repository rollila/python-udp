from threading import Timer
import copy
import math
import pickle
import struct
import server_to_client
import shared_utils


class StateBroadcaster:

    def __init__(self, clients, sock, max_bytes_per_sec, target_object_number, max_players, address, port):
        self.clients = clients
        self.sock = sock
        self.max_bytes_per_sec = max_bytes_per_sec
        self.target_object_number = target_object_number
        self.updates_per_sec = 60
        self.update_increase_timer = None
        self.max_players = max_players
        self.address = address
        self.port = port

        self.timer = Timer(1 / self.updates_per_sec, self.broadcast_state)
        self.timer.start()

    def broadcast_state(self):
        print('\033[H\033[J')
        print('Server running at {} port {}'.format(self.address, self.port))
        print('Maximum allowed bandwidth: {} bytes/sec'.format(self.max_bytes_per_sec))
        print('Target number of objects per update: {} '.format(
            self.target_object_number))
        print('Updating at {} messages per second, max message size: {} bytes'.format(
            self.updates_per_sec, self.bytes_per_message()))
        print('Number of connected players: {} / {}'.format(
            len(self.clients.players), self.max_players))
        clients = self.clients.get_clients()
        sock = self.sock
        messages = []

        for player_id in clients:
            try:
                client = clients[player_id]
                address = client.address
                message = self.build_message(player_id)
                messages.append((address, message))
            except:
                self.updates_per_sec -= 1
                self.init_increase_updates_timer()
                self.timer = Timer(1 / self.updates_per_sec,
                                   self.broadcast_state)
                self.timer.start()

                return

        for (address, message) in messages:
            sock.sendto(message, address)

        for player_id in clients:
            clients[player_id].last_sent_seq += 1

        self.timer = Timer(1 / self.updates_per_sec, self.broadcast_state)
        self.timer.start()

    def build_message(self, player_id):
        clients = self.clients.get_clients()
        message = [clients[player_id].last_sent_seq]

        item_size = server_to_client.item_size()
        current_size = len(pickle.dumps(message))

        sorted_players = self.sort_by_proximity(
            clients[player_id].player_state, clients)

        for target_player in sorted_players:
            if (current_size + item_size > self.bytes_per_message()):
                if (len(message) < self.target_object_number + 1):
                    raise RuntimeError('Could not reach target object number')
                else:
                    break

            if (target_player.id == player_id):
                continue

            state = server_to_client.serialize(
                target_player.id, target_player.location)

            message.append(state)
            current_size += item_size

        return pickle.dumps(message)

    def sort_by_proximity(self, origin_player, clients):
        player_states = []
        for player_id in clients:
            player_states.append(clients[player_id].player_state)

        return sorted(player_states, key=lambda player: shared_utils.distance(origin_player.location, player.location))

    def bytes_per_message(self):
        return math.floor(self.max_bytes_per_sec / max(1, len(self.clients.players)) / self.updates_per_sec)

    def increase_updates_per_sec(self):
        self.updates_per_sec += 1
        if (self.updates_per_sec < 60):
            self.init_increase_updates_timer()

    def init_increase_updates_timer(self):
        if (self.update_increase_timer != None):
            self.update_increase_timer.cancel()
        self.update_increase_timer = Timer(1, self.increase_updates_per_sec)
        self.update_increase_timer.start()
