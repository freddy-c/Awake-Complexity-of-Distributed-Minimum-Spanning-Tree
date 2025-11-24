from collections import deque
from baseline.shared import Procedure, TransmissionRound


def merge_down(self, start_round: int):
    self.logger.info(f"initializing Merge Down starting at round {start_round}.")

    base = start_round - 1

    if self.valid_moe:
        if self.root:
            schedule_items = [
                (1 + base, Procedure.MERGE_DOWN, TransmissionRound.DOWN_SEND),
                (
                    2 * self.n + 3 + base,
                    Procedure.MERGE_DOWN,
                    TransmissionRound.END,
                ),
            ]
        else:
            schedule_items = [
                (
                    self.i + base,
                    Procedure.MERGE_DOWN,
                    TransmissionRound.DOWN_RECEIVE,
                ),
                (
                    self.i + 1 + base,
                    Procedure.MERGE_DOWN,
                    TransmissionRound.DOWN_SEND,
                ),
                (
                    2 * self.n + 3 + base,
                    Procedure.MERGE_DOWN,
                    TransmissionRound.END,
                ),
            ]
    else:
        schedule_items = [
            (
                2 * self.n + 3 + base,
                Procedure.MERGE_DOWN,
                TransmissionRound.END,
            )
        ]

    # Populate the schedule queue
    self.schedule = deque(schedule_items)
    if self.schedule:
        next_round, _, _ = self.schedule[0]
        if next_round > start_round:
            self.sleep(next_round)


def _merge_down_handler(self, phase: TransmissionRound):
    if phase == TransmissionRound.DOWN_RECEIVE:
        self.logger.info("is handling DOWN_RECEIVE.")
    elif phase == TransmissionRound.DOWN_SEND:
        self.logger.info("is handling DOWN_SEND.")

        # TODO: if v’s NEW-LEVEL-NUM is non-empty and it receives a non-empty value from its parent, v updates its NEW-LEVEL-NUM to that value plus one.
        # TODO: Similarly, if v’s NEW-FRAGMENT-ID is non-empty and it receives a non-empty value from its parent, v updates its NEW-FRAGMENT-ID to that value.

        if self.inbox and self.new_level_num is None:
            port, message = self.inbox[0]
            new_level_num, new_fragment_id = message.values()
            self.new_level_num = new_level_num + 1
            self.new_fragment_id = new_fragment_id
            self.new_parent_port = port
            self.new_child_ports = self.child_ports[:]

            self.inbox.clear()

        # sends down the value of its NEW-LEVEL-NUM and also the value of its NEW-FRAGMENT-ID.
        message = {
            "new_level_num": self.new_level_num,
            "new_fragment_id": self.new_fragment_id,
        }

        for port in self.child_ports:
            self.send_message(port, message)
            self.logger.info(f"sent: {message} to child via port {port}.")
