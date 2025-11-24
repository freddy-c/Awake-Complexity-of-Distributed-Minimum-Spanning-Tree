from optimized.shared import Stage


def broadcast_moe_entry(self, round_number):
    if self.root:
        if self.upcast_value == float("inf"):
            self.fragment_broadcast(round_number + 1, "TERMINATE")

        else:
            self.fragment_broadcast(round_number + 1, self.upcast_value)
            self.logger.info(
                f"is root and will broadcast the MOE value which is {self.upcast_value}"
            )
    else:
        self.fragment_broadcast(round_number + 1)


def broadcast_moe_exit(self):
    if self.broadcast_message == "TERMINATE":
        self.stage = Stage.TERMINATED
        self.terminated = True
        return

    if self.local_moe_port is not None:
        if float(self.broadcast_message) == float(
            self.ports[self.local_moe_port]["weight"]
        ):
            self.logger.info(
                f"has a MOE of weight {self.ports[self.local_moe_port]['weight']} which is equal to the weight of the fragment MOE which is {self.broadcast_message} "
            )

            self.is_fragment_moe = True
        else:
            self.is_fragment_moe = False
    else:
        self.is_fragment_moe = False

    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )
