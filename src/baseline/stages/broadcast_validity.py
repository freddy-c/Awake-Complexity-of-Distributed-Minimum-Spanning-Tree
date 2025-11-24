def broadcast_validity_entry(self, round_number):
    if self.root:
        self.fragment_broadcast(round_number + 1, self.valid_moe)
        self.logger.info(
            f"is root and will broadcast the validity of the MOE which is: {'valid' if self.valid_moe else 'invalid'}"
        )
    else:
        self.fragment_broadcast(round_number + 1)


def broadcast_validity_exit(self):
    self.logger.info(
        f"the fragment MOE is {'valid' if self.broadcast_message else 'invalid'}"
    )

    self.valid_moe = self.broadcast_message

    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )
