class Vertex:
    def __init__(self, vertex_id, status):
        self.vertex_id = vertex_id
        self.status = status

    def __eq__(self, vert):
        return hasattr(vert, "vertex_id") and self.vertex_id == vert.vertex_id

    def __hash__(self):
        return hash(self.vertex_id)
