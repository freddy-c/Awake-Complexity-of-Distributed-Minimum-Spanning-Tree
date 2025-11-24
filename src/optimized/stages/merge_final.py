def merge_final_entry(self, round_number):
    self.merge_down(round_number + 1)


def merge_final_exit(self):
    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )

    self.logger.info(
        f'have "new_fragment_id": {self.new_fragment_id}, "new_level_number": {self.new_level_num}\''
    )

    # updates its fragment ID to NEW-FRAGMENT-ID and updates its level number to NEW-LEVEL-NUM assuming they're non-empty
    if self.new_fragment_id is not None:
        self.fragment_id = self.new_fragment_id
        self.i = self.new_level_num

        # clear those variables in preparation for the next phase
        self.new_fragment_id = None
        self.new_level_num = None

        self.root = False

        # if self.new_parent_port is not None:
        self.parent_port = self.new_parent_port

        self.new_parent_port = None

        self.child_ports = self.new_child_ports[:]  # create a shallow copy
        self.new_child_ports.clear()

    self.inbox.clear()

    # self.logger.info("-" * 300)
    # self.print_state()
