from collections import deque
from baseline.shared import Procedure, TransmissionRound


def transmit_neighbor(self, start_round: int, message):
    """
    Initialize the Transmit Neighbor procedure to send a message to neighboring nodes.
    :param start_round: The round to start the procedure.
    :param value: The value to be transmitted to neighbors.
    """
    self.logger.info(f"initializing Transmit Neighbor starting at round {start_round}.")

    self.neighbor_message = message  # Set the value to be transmitted
    base = start_round

    # Schedule phases for transmitting to neighbors
    schedule_items = [
        (
            self.i + base,
            Procedure.TRANSMIT_NEIGHBOR,
            TransmissionRound.DOWN_RECEIVE,
        ),
        (
            self.i + 1 + base,
            Procedure.TRANSMIT_NEIGHBOR,
            TransmissionRound.DOWN_SEND,
        ),
        (
            2 * self.n - self.i + 1 + base,
            Procedure.TRANSMIT_NEIGHBOR,
            TransmissionRound.UP_RECEIVE,
        ),
        (
            2 * self.n - self.i + 2 + base,
            Procedure.TRANSMIT_NEIGHBOR,
            TransmissionRound.UP_SEND,
        ),
        (
            2 * self.n + 3 + base,
            Procedure.TRANSMIT_NEIGHBOR,
            TransmissionRound.END,
        ),
    ]

    # Populate the schedule queue
    self.schedule = deque(schedule_items)
    if self.schedule:
        next_round, _, _ = self.schedule[0]
        if next_round > start_round:
            self.sleep(next_round)


def _transmit_neighbor_handler(self, phase: TransmissionRound):
    """Handle transmit-neighbor-specific behavior."""
    if phase == TransmissionRound.DOWN_SEND:
        for (
            port,
            message,
        ) in self.inbox:  # Assuming inbox contains (port, message) pairs
            self.received_neighbor_messages[port] = message
            self.logger.info(f"received {message} from port {port}.")

        self.inbox.clear()

        # transmit message to children
        for port in self.child_ports:
            self.send_message(port, self.neighbor_message)
            self.logger.info(
                f"sent value {self.neighbor_message} to child via port {port}."
            )
    if phase == TransmissionRound.UP_SEND:
        for (
            port,
            message,
        ) in self.inbox:  # Assuming inbox contains (port, message) pairs
            self.received_neighbor_messages[port] = message
            self.logger.info(f"received {message} from port {port}.")

        self.inbox.clear()

        # transmit message to parent
        if self.parent_port is not None:
            self.send_message(self.parent_port, self.neighbor_message)
            self.logger.info(
                f"sent value {self.neighbor_message} to parent via port {self.parent_port}."
            )

    if phase == TransmissionRound.DOWN_RECEIVE:
        # TODO: listen for message from parent
        pass
    if phase == TransmissionRound.UP_RECEIVE:
        # TODO: listen to message from children
        pass
    elif phase == TransmissionRound.END:
        self.logger.info("is in END round.")
