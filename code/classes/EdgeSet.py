
class EdgeSet:

    def __init__(self):
        self.edges = set()
        self.nodes = set()

    def add_edge(self, vertex_from, vertex_to):
        self.nodes.add(vertex_from)
        self.nodes.add(vertex_to)
        self.edges.update([(vertex_from, vertex_to), (vertex_to, vertex_from)])

    def list_rep(self):
        return list(self.edges)