def update_schedule_depth_entry(self, round_number):
    self.logger.info("Update Schedule Depth Entry Method")

    self.flood_max(round_number + 1)


def update_schedule_depth_exit(self):
    result = None

    if self.inbox:
        result = result = max(*[message for _, message in self.inbox], self.i)
        self.maximum_depth = result

    self.phase += 1
    self.logger.info("Maximum depth is %s", self.maximum_depth)
    self.print_state()
    self.logger.info("-" * 200)
