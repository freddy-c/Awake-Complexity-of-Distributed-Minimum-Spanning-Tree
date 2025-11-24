from collections import deque
from baseline.shared import Procedure, TransmissionRound


def transmit_adjacent(self, start_round: int, message):
    """
    Initialize the Transmit Adjacent procedure to send a message to adjacent nodes not in the tree.
    :param start_round: The round to start the procedure.
    :param message: The message to be transmitted to adjacent nodes.
    """
    self.logger.info(f"initializing Transmit Adjacent starting at round {start_round}.")

    self.adjacent_message = message  # Set the message to be transmitted
    base = start_round

    # Schedule phases for transmitting to adjacent neighbors
    schedule_items = [
        (
            self.n + 1 + base,
            Procedure.TRANSMIT_ADJACENT,
            TransmissionRound.SIDE_SEND_RECEIVE,
        ),
        (
            2 * self.n + 3 + base,
            Procedure.TRANSMIT_ADJACENT,
            TransmissionRound.END,
        ),
    ]

    # Populate the schedule queue
    self.schedule = deque(schedule_items)
    if self.schedule:
        next_round, _, _ = self.schedule[0]
        if next_round > start_round:
            self.sleep(next_round)


def _transmit_adjacent_handler(self, phase: TransmissionRound):
    if phase == TransmissionRound.SIDE_SEND_RECEIVE:
        # transmit message to neighbors not in the tree
        ports = [
            port
            for port in self.ports.keys()
            if port != self.parent_port and port not in self.child_ports
        ]

        for port in ports:
            self.send_message(port, self.adjacent_message)
            self.logger.info(f"sent value {self.adjacent_message} via port {port}.")
