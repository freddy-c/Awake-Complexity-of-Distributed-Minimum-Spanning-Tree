from baseline.shared import EdgeState, Flip


def transmit_adjacent_state_entry(self, round_number):
    self.transmit_adjacent(
        round_number + 1,
        {"fragment_id": self.fragment_id, "level_number": self.i},
    )

    self.logger.info(
        f'will transmit their state which is "fragment_id": {self.fragment_id}, "level_number": {self.i}'
    )


def transmit_adjacent_state_exit(self):
    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )

    self.new_fragment_id = None
    self.new_level_num = None

    # These are the conditions for the node to be u_T
    if self.is_fragment_moe and self.valid_moe:
        # Find message from node on other end of the valid MOE
        for port, message in self.inbox:
            if port == self.local_moe_port:
                # set this valid MOE as a BRANCH edge
                self.ports[self.local_moe_port]["state"] = EdgeState.BRANCH

                self.new_fragment_id = message["fragment_id"]
                self.new_level_num = message["level_number"] + 1

                self.logger.info(
                    f'have "new_fragment_id": {self.new_fragment_id}, "new_level_number": {self.new_level_num}\''
                )

                self.new_parent_port = self.local_moe_port

                self.new_child_ports = (
                    [self.parent_port] if self.parent_port is not None else []
                ) + self.child_ports

                break

    if self.fragment_flip == Flip.HEAD:
        for port, message in self.inbox:
            edge_weight = self.ports[port]["weight"]
            if (
                edge_weight == self.adjacent_moe[port]
                and self.adjacent_flip[port] == Flip.TAIL
            ):
                self.child_ports.append(port)

                # we U_H can now set this edge to be a branch edge as it meets all conditions for being an MOE
                # i.e. its the MOE of the other fragment and its valid because we're HEADS and they're TAILS
                self.ports[port]["state"] = EdgeState.BRANCH

    # identify fragment internal edges
    for port, message in self.inbox:
        if message["fragment_id"] == self.fragment_id:
            # internal edge
            self.ports[port]["state"] = EdgeState.REJECTED

    self.inbox.clear()
