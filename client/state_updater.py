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
        self.moving = False
        self.directions = ['left', 'up', 'right', 'down']
        self.direction = random.choice(self.directions)
        self.timer = Timer(1 / updates_per_second, self.update_state)
        self.timer.start()

    def gen_new_state(self):
        rnd = random.random()
        if (rnd < 0.1):
            self.moving = not self.moving

        location = self.state['location']

        if (self.moving == False):
            return {'location': location}

        rnd = random.random()
        if (rnd < 0.2):
            self.direction = random.choice(self.directions)

        x = location[0]
        y = location[1]

        if (self.direction == 'left'):
            x = max(0, location[0] - 1)
        elif (self.direction == 'right'):
            x = location[0] + 1
        elif (self.direction == 'up'):
            y = max(0, location[1] - 1)
        elif (self.direction == 'down'):
            y = location[1] + 1

        new_state = {
            'location': (x, y)
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
