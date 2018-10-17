from threading import Timer
import copy
import pickle
import struct


class StateBroadcaster:

    def __init__(self, clients, sock, max_bytes_per_sec, target_object_number):
        self.clients = clients
        self.sock = sock
        self.max_bytes_per_sec = max_bytes_per_sec
        self.target_object_number = target_object_number
        self.updates_per_sec = 60
        self.update_increase_timer = None

        self.timer = Timer(1 / self.updates_per_sec, self.broadcast_state)
        self.timer.start()

    def broadcast_state(self):
        print('Updating at {} messages per second, max message size: {}'.format(
            self.updates_per_sec, self.bytes_per_message()))
        clients = self.clients
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
        clients = self.clients
        message = [clients[player_id].last_sent_seq]

        item_size = struct.calcsize('III')
        current_size = len(pickle.dumps(message))

        sorted_players = self.sort_by_proximity(
            clients[player_id].player_state, clients)

        for target_player in sorted_players:
            print(target_player)
            if (current_size + item_size > self.bytes_per_message()):
                if (len(message) < self.target_object_number):
                    raise RuntimeError('Could not reach target object number')
                else:
                    break

            if (target_player.id == player_id):
                continue

            state = struct.pack('III', target_player.id,
                                target_player.location[0], target_player.location[1])
            message.append(state)
            current_size += item_size

        print(message)

        return pickle.dumps(message)

    def sort_by_proximity(self, origin_player, clients):
        player_states = []
        for player_id in clients:
            player_states.append(clients[player_id].player_state)

        return sorted(player_states, key=lambda player: abs(origin_player.location[0] - player.location[0]) + abs(origin_player.location[1] - player.location[1]))

    def bytes_per_message(self):
        return self.max_bytes_per_sec / max(1, len(self.clients)) / self.updates_per_sec

    def increase_updates_per_sec(self):
        self.updates_per_sec += 1
        if (self.updates_per_sec < 60):
            self.init_increase_updates_timer()

    def init_increase_updates_timer(self):
        if (self.update_increase_timer != None):
            self.update_increase_timer.cancel()
        self.update_increase_timer = Timer(1, self.increase_updates_per_sec)
        self.update_increase_timer.start()
