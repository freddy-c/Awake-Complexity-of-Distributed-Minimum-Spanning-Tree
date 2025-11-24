from baseline.shared import EdgeState


def upcast_moe_entry(self, round_number):
    moe = min(
        (
            (port, details["weight"])
            for port, details in self.ports.items()
            if port != self.parent_port
            and port not in self.child_ports
            and details["state"] != EdgeState.REJECTED
        ),
        default=(None, float("inf")),
        key=lambda x: x[1],
    )

    self.local_moe_port = moe[0]
    self.logger.info(f"local MOE on port {self.local_moe_port}")

    self.upcast_min(round_number + 1, moe[1])


def upcast_moe_exit(self):
    if self.root:
        self.logger.info(f"ROOT: upcast min value is {self.upcast_value}")

    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )
