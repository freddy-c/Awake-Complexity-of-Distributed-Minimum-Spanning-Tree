from collections import deque
from baseline.shared import Procedure, TransmissionRound


def fragment_broadcast(self, start_round: int, message: str = None):
    """
    Initialize the Fragment Broadcast procedure with a given message.
    :param start_round: The round to start the procedure.
    :param message: The initial message for the broadcast.
    """
    self.logger.info(
        f"initializing Fragment Broadcast starting at round {start_round}."
    )

    self.broadcast_message = (
        message if self.root else None
    )  # Set broadcast value for root

    base = start_round - 1

    if self.root:
        schedule_items = [
            (1 + base, Procedure.FRAGMENT_BROADCAST, TransmissionRound.DOWN_SEND),
            (
                2 * self.n + 3 + base,
                # self.n + 1 + base,
                Procedure.FRAGMENT_BROADCAST,
                TransmissionRound.END,
            ),
        ]
    else:
        schedule_items = [
            (
                self.i + base,
                Procedure.FRAGMENT_BROADCAST,
                TransmissionRound.DOWN_RECEIVE,
            ),
            (
                self.i + 1 + base,
                Procedure.FRAGMENT_BROADCAST,
                TransmissionRound.DOWN_SEND,
            ),
            (
                2 * self.n + 3 + base,
                # self.n + 1 + base,
                Procedure.FRAGMENT_BROADCAST,
                TransmissionRound.END,
            ),
        ]

    # Populate the schedule queue
    self.schedule = deque(schedule_items)
    if self.schedule:
        next_round, _, _ = self.schedule[0]
        if next_round > start_round:
            self.sleep(next_round)


# Procedure-specific handlers
def _fragment_broadcast_handler(self, phase: TransmissionRound):
    """Handle fragment-broadcast-specific behavior."""
    if phase == TransmissionRound.DOWN_RECEIVE:
        self.logger.info("is handling DOWN_RECEIVE.")
    elif phase == TransmissionRound.DOWN_SEND:
        self.logger.info("is handling DOWN_SEND.")

        if self.inbox:
            _, message = self.inbox[0]
            self.broadcast_message = message  # Update the broadcast value

        self.inbox.clear()

        for port in self.child_ports:
            self.send_message(port, self.broadcast_message)
            self.logger.info(
                f"sent value {self.broadcast_message} to child via port {port}."
            )
    elif phase == TransmissionRound.END:
        self.logger.info("is in END round.")
