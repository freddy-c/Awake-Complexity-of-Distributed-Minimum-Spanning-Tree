from abc import ABC, abstractmethod
from typing import Tuple, List, Dict
import logging


class Node(ABC):
    def __init__(self, node_id: int, verbose: bool = False):
        self.node_id = node_id

        self.logger = logging.getLogger(f"Node {self.node_id}")
        log_level = logging.DEBUG if verbose else logging.WARNING
        self.logger.setLevel(log_level)

        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        self.ports: Dict[int, Dict] = (
            {}
        )  # Ports dictionary (port ID -> edge attributes)
        self.inbox: List[Tuple[int, str]] = (
            []
        )  # List of incoming messages (port_id, message)
        self.staging_inbox: List[Tuple[int, str]] = []

        self.sleeping: bool = False
        self.wake_round: int = 1
        self.deferred_sleep: int = (
            -1
        )  # Round in which the node will sleep after processing
        self.terminated: bool = False
        self.awake_rounds: int = 0
        self.rounds: int = 0

    def __repr__(self):
        return f"Node(node_id={self.node_id}, ports={len(self.ports)})"

    def send_message(self, port_id: int, message: str):
        """Send a message through a specific port."""
        if port_id not in self.ports:
            raise ValueError(f"Invalid port ID {port_id} for Node {self.node_id}.")

        destination: Node = self.ports[port_id]["destination"]
        destination_port: int = self.ports[port_id]["destination_port"]

        # (port, message) where its the port that connects them to this node
        destination.staging_inbox.append((destination_port, message))

    def sleep(self, wake_round: int):
        """Defer sleeping until the end of the current round."""
        if wake_round <= 0:
            raise ValueError("Wake-up round must be a positive integer.")
        self.deferred_sleep = wake_round

    def finalize_sleep(self, current_round: int):
        """Put the node to sleep if a deferred sleep is scheduled."""
        if self.deferred_sleep > current_round:
            self.sleeping = True
            self.wake_round = self.deferred_sleep

    def wake_up(self):
        """Wake the node up."""
        self.sleeping = False
        self.wake_round = -1

    def compute(self, round_number: int):
        """Handle sleeping/waking logic and delegate execution to the concrete class."""
        if self.sleeping:
            if round_number >= self.wake_round:
                self.wake_up()
            else:
                return

        # Delegate to the concrete class to execute the current phase and schedule the next wake-up
        self._compute(round_number)
        self.awake_rounds += 1

    @abstractmethod
    def _compute(self, round_number: int):
        """Abstract method to be implemented by subclasses."""
        pass
