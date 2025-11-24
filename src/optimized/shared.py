from enum import Enum


class Procedure(Enum):
    FRAGMENT_BROADCAST = "Fragment-Broadcast"
    UPCAST_MIN = "Upcast-Min"
    TRANSMIT_NEIGHBOR = "Transmit-Neighbor"
    TRANSMIT_ADJACENT = "Transmit-Adjacent"
    MERGE_UP = "Merge-Up"
    MERGE_DOWN = "Merge-Down"
    FLOOD_MAXIMUM_DEPTH = "Flood-Maximum-Depth"


class TransmissionRound(Enum):
    DOWN_RECEIVE = "Down-Receive"
    DOWN_SEND = "Down-Send"
    SIDE_SEND_RECEIVE = "Side-Send-Receive"
    UP_RECEIVE = "Up-Receive"
    UP_SEND = "Up-Send"
    END = "End"


class EdgeState(Enum):
    BASIC = "basic"
    BRANCH = "branch"
    REJECTED = "rejected"


class Stage(Enum):
    FIND_MOE = "Find-MOE"
    UPCAST_MOE = "Upcast-MOE"
    BROADCAST_MOE = "Broadcast-MOE"
    TRANSMIT_ADJACENT_MOE = "Transmit-Adjacent-MOE"
    COIN_FLIP_BROADCAST = "Coin-Flip-Broadcast"
    TRANSMIT_ADJACENT_FLIP = "Transmit-Adjacent-Flip"
    UPCAST_VALIDITY = "Upcast-Validity"
    BROADCAST_VALIDITY = "Broadcast-Validity"
    TRANSMIT_ADJACENT_STATE = "Transmit-Adjacent-State"
    MERGE_INITIAL = "Merge-Initial"
    MERGE_FINAL = "Merge-Final"
    TERMINATED = "Terminated"
    UPDATE_SCHEDULE_DEPTH = "Update-Schedule-Depth"


class Flip(Enum):
    HEAD = "Head"
    TAIL = "Tail"
