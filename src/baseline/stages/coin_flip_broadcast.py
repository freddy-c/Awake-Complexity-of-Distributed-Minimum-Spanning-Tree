import random
from baseline.shared import Flip


def coin_flip_broadcast_entry(self, round_number):
    if self.root:
        coin_flip = random.choice([Flip.HEAD, Flip.TAIL])

        self.fragment_broadcast(round_number + 1, coin_flip)
        self.logger.info(
            f"is root and will broadcast the coin flip result which is {coin_flip}"
        )
    else:
        self.fragment_broadcast(round_number + 1)


def coin_flip_broadcast_exit(self):
    self.logger.info(
        f"Node {self.node_id}, the fragment is a {self.broadcast_message} fragment"
    )

    self.fragment_flip = self.broadcast_message

    self.logger.info(
        f"has finished stage {self.stage}. It must now handle any logic and change stage."
    )
