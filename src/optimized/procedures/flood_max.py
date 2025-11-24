from collections import deque
from optimized.shared import Procedure, TransmissionRound


def flood_max(self, start_round: int):
    self.logger.info("Initializing Flood Maximum Depth start at round %s", start_round)

    base = start_round

    schedule_items = [
        (
            base,
            Procedure.FLOOD_MAXIMUM_DEPTH,
            TransmissionRound.SIDE_SEND_RECEIVE,
        ),
        (
            base + 1,
            Procedure.FLOOD_MAXIMUM_DEPTH,
            TransmissionRound.SIDE_SEND_RECEIVE,
        ),
        (
            base + 2,
            Procedure.FLOOD_MAXIMUM_DEPTH,
            TransmissionRound.SIDE_SEND_RECEIVE,
        ),
        (
            base + 3,
            Procedure.FLOOD_MAXIMUM_DEPTH,
            TransmissionRound.END,
        ),
    ]

    # Populate the schedule queue
    self.schedule = deque(schedule_items)
    if self.schedule:
        next_round, _, _ = self.schedule[0]
        if next_round > start_round:
            self.sleep(next_round)


def _flood_max_handler(self, phase: TransmissionRound):
    if phase == TransmissionRound.SIDE_SEND_RECEIVE:
        if self.inbox:
            result = result = max(*[message for _, message in self.inbox], self.i)
        else:
            result = self.i

        for port in self.ports:
            self.send_message(port, result)
            self.logger.info("Sent maximum depth %s to port %s", result, port)

        self.maximum_depth = result
        self.inbox.clear()
