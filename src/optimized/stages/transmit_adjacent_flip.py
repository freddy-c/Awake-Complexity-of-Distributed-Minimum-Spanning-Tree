from optimized.shared import Flip


def transmit_adjacent_flip_entry(self, round_number):
    self.transmit_adjacent(round_number + 1, self.broadcast_message)

    self.logger.info(f"will transmit the FLIP value which is {self.broadcast_message}")


def transmit_adjacent_flip_exit(self):
    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )

    self.adjacent_flip.clear()

    for port, message in self.inbox:
        self.adjacent_flip[port] = message

    self.logger.info(f"Node {self.node_id}: {self.adjacent_flip}")

    status = False

    # does this node have the MOE? If not ignore
    if self.is_fragment_moe:
        self.logger.info(f"Node {self.node_id}: {self.fragment_flip}")

        if self.fragment_flip == Flip.TAIL:
            # iterate through the messages received from adjacent nodes not in the fragment
            for (
                port,
                message,
            ) in self.inbox:
                # find the flip of the fragment which contains the node that is the destination of the MOE
                if port == self.local_moe_port and message == Flip.HEAD:
                    status = True

                    break

    self.valid_moe = status

    if status is False:
        self.logger.info("Invalid")
    else:
        self.logger.info("Valid")

    self.inbox.clear()
