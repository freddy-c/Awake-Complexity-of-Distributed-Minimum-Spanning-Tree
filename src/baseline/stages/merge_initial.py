def merge_initial_entry(self, round_number):
    self.merge_up(round_number + 1)


def merge_initial_exit(self):
    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )

    self.logger.info(
        f'have "new_fragment_id": {self.new_fragment_id}, "new_level_number": {self.new_level_num}\''
    )
