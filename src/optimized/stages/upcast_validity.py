def upcast_validity_entry(self, round_number):
    self.upcast_min(round_number + 1, 0 if self.valid_moe else 1)


def upcast_validity_exit(self):
    if self.root:
        self.logger.info(
            f"Node {self.node_id}, the fragment MOE is {'invalid' if int(self.upcast_value) else 'valid'}"
        )

        self.valid_moe = True if not int(self.upcast_value) else False

    self.logger.info(
        f"has finished {self.stage}. It must now handle any logic and change stage."
    )
