from enum import Enum


class VertexStatus(Enum):
    NOT_BURNED = 0
    # Neighbours of Burning vertices can be Burned, Not Burned, or Burning.
    BURNING = 1
    # All neighbors of the vertex are either Burning or are also Burned
    # nothing uses BURNED yet, could be nice to use as an optimization
    BURNED = 2
    DOESNT_EXIST = 3


class Vertex:
    def __init__(self, vertex_id, status):
        self.vertex_id = vertex_id
        self.status = status

    def __eq__(self, vert):
        return hasattr(vert, "vertex_id") and self.vertex_id == vert.vertex_id

    def __hash__(self):
        return hash(self.vertex_id)
