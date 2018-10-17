import random
from threading import Timer
import client_to_server


class StateUpdater:

    def __init__(self, sock, updates_per_second, state, server_address):
        self.sock = sock
        self.server_address = server_address
        self.state = state
        self.seq_nr = 0
        self.updates_per_second = updates_per_second
        self.timer = Timer(1 / updates_per_second, self.update_state)
        self.timer.start()

    def gen_new_state(self):
        location = self.state['location']
        new_location = (location[0] + 1, location[1] + 1)
        new_state = {
            'location': new_location
        }

        return new_state

    def update_state(self):
        self.seq_nr += 1
        new_state = self.gen_new_state()
        self.state['location'] = new_state['location']

        message = client_to_server.serialize(
            self.seq_nr, self.state['id'], self.state['location'])

        self.sock.sendto(message, self.server_address)

        self.timer = Timer(0.1, self.update_state)
        self.timer.start()
