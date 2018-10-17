import time


class ClientState:

    def __init__(self, address, player_state):
        self.address = address
        self.player_state = player_state
        self.last_received_seq = 0
        self.last_sent_seq = 0
        self.last_received_timestamp = time.time()
        self.disconnected = False
