from collections import deque
from optimized.shared import Procedure, TransmissionRound


def upcast_min(self, start_round: int, value: int):
    """
    Initialize the Upcast Min procedure.
    :param start_round: The round to start the procedure.
    """
    self.logger.info(f"initializing Upcast Min starting at round {start_round}.")

    self.upcast_value = value  # Set the value to be upcasted
    base = start_round - 1

    schedule_items = [
        (
            self.maximum_depth - self.i + 2 + base,  # OPTIMIZATION
            Procedure.UPCAST_MIN,
            TransmissionRound.UP_RECEIVE,
        ),
        (
            self.maximum_depth - self.i + 3 + base,  # OPTIMIZATION
            Procedure.UPCAST_MIN,
            TransmissionRound.UP_SEND,
        ),
        (
            self.maximum_depth + 4 + base,
            Procedure.UPCAST_MIN,
            TransmissionRound.END,
        ),  # OPTIMIZATION
    ]

    # Populate the schedule queue
    self.schedule = deque(schedule_items)
    if self.schedule:
        next_round, _, _ = self.schedule[0]
        if next_round > start_round:
            self.sleep(next_round)


def _upcast_min_handler(self, phase: TransmissionRound):
    """Handle upcast-min-specific behavior."""
    if phase == TransmissionRound.UP_RECEIVE:
        self.logger.info(f"UP_RECEIVE.")
        self.logger.info(f"is trying to upcast {self.upcast_value}")
    elif phase == TransmissionRound.UP_SEND:
        self.logger.info(f"UP_SEND.")
        # compares the messages it previously received in its Up-Receive round to its current messagee, if any, and stores the minimum value
        if self.inbox:
            # Extract all message values from the inbox
            received_values = [float(message) for _, message in self.inbox]
            # Find the smallest value
            smallest_received = min(received_values)
            self.upcast_value = min(smallest_received, self.upcast_value)

        self.inbox.clear()

        if self.root:
            self.logger.info(
                f"Node {self.node_id}, upcasted minimum value: {self.upcast_value}"
            )

        # transmits this minimum value to its parent in the tree
        elif self.parent_port is not None:
            self.send_message(self.parent_port, str(self.upcast_value))
            self.logger.info(
                f"sent value {self.upcast_value} to parent via port {self.parent_port}."
            )

    elif phase == TransmissionRound.END:
        self.logger.info("is in END round.")
