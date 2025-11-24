from collections import deque
from optimized.shared import Procedure, TransmissionRound


def merge_up(self, start_round: int):
    self.logger.info(f"initializing Merge Up starting at round {start_round}.")

    base = start_round - 1

    if self.valid_moe:
        schedule_items = [
            (
                self.maximum_depth - self.i + 2 + base,  # OPTIMIZED
                Procedure.MERGE_UP,
                TransmissionRound.UP_RECEIVE,
            ),
            (
                self.maximum_depth - self.i + 3 + base,  # OPTIMIZED
                Procedure.MERGE_UP,
                TransmissionRound.UP_SEND,
            ),
            (self.maximum_depth + 4 + base, Procedure.MERGE_UP, TransmissionRound.END),  # OPTIMIZED
        ]
    else:
        schedule_items = [
            (self.maximum_depth + 4 + base, Procedure.MERGE_UP, TransmissionRound.END),  # OPTIMIZED
        ]

    # Populate the schedule queue
    self.schedule = deque(schedule_items)
    if self.schedule:
        next_round, _, _ = self.schedule[0]
        if next_round > start_round:
            self.sleep(next_round)


def _merge_up_handler(self, phase: TransmissionRound):
    if phase == TransmissionRound.UP_RECEIVE:
        self.logger.info("UP_RECEIVE.")
        self.logger.info(
            f"is trying to upcast {self.new_fragment_id, self.new_level_num}"
        )
    if phase == TransmissionRound.UP_SEND:
        # TODO: if v receives a non-empty NEW-LEVEL-NUM from its child, v sets its own NEW-LEVEL-NUM to the received value plus one.
        # TODO: Similarly, if v receives a non-empty NEW-FRAGMENT-ID, v sets its own NEW-FRAGMENT-ID to that value.
        # TODO: if v receives a non-empty NEW-LEVEL-NUM, from its child, it records internally that its child will be its new parent and its neighbors in T will be its children.

        self.logger.info(self.inbox)
        if self.inbox:
            for port, message in self.inbox:
                self.logger.info(f"Node {self.node_id}: message: {message}")
                if message["new_level_num"] is not None:
                    self.new_level_num = message["new_level_num"] + 1
                    self.new_fragment_id = message["new_fragment_id"]

                    # If you receive this here the child received from is the new parent
                    # Old parent and any of the other children now become children
                    self.new_parent_port = port

                    #  if v receives a non-empty NEW-LEVEL-NUM, from its child, it records internally that its child will be its new parent and its neighbors in T will be its children.
                    self.new_child_ports = [
                        neighbor for neighbor in self.child_ports if neighbor != port
                    ] + ([self.parent_port] if self.parent_port is not None else [])

                    # self.logger.info(self.child_ports)

                    break

            self.inbox.clear()

        # sends up the value in its NEW-LEVEL-NUM and NEW-FRAGMENT-ID
        message = {
            "new_level_num": self.new_level_num,
            "new_fragment_id": self.new_fragment_id,
        }

        self.logger.info(f"Node {self.node_id}: new state: {message}")

        if self.parent_port is not None:
            self.send_message(self.parent_port, message)

            self.logger.info(
                f"sent state {message} to parent via port {self.parent_port}."
            )
