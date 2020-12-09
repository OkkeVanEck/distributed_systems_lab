from enum import Enum


class VertexStatus(Enum):
    NOT_BURNED = 0
    # Neighbours of Burning vertices can be Burned, Not Burned, or Burning.
    BURNING = 1
    # All neighbors of the vertex are either Burning or are also Burned
    # nothing uses BURNED yet, could be nice to use as an optimization
    BURNED = 2
    DOESNT_EXIST = 3


class MPI_TAG(Enum):
    FROM_COMPUTE_TO_COMPUTE = 1
    FROM_HEADNODE_TO_COMPUTE = 2
    HEARTBEAT = 3
    RESET = 4
    KILL = 5
    CONTINUE = 6

class SLEEP_TIMES(Enum):
    COMPUTE_NODE_LISTEN_SLEEP = 0.05
    COMPUTE_NODE_SEND_HEARTBEAT = 1
    COMPUTE_NODE_MANAGE_FIRES = 0.1
