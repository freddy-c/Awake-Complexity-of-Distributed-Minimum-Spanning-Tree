def transmit_adjacent_moe_entry(self, round_number):
    self.transmit_adjacent(round_number + 1, self.broadcast_message)


def transmit_adjacent_moe_exit(self):
    self.adjacent_moe.clear()

    if self.inbox:
        for port, message in self.inbox:
            self.adjacent_moe[port] = message

    self.inbox.clear()
