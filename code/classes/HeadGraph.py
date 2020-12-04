

class HeadGraph:
    def __init__(self, total_vertices, out_e, out_v):
        self.base_id = 0
        self.total_vertices = total_vertices;
        self.prev_vertices = 0
        self.vertices = set()
        self.vert_in_file = set()
        self.edges = set()
        self.edges_in_file = set()

    def get_sample_vertices(self):
        return self.get_num_vertices() - self.prev_vertices

    def get_num_vertices(self):
        return len(vertices)

    def add_edge(self, vertex_from: int, vertex_to: int, base_id=self.base_id):
        src = vertex_from + base_id
        dest = vertex_to + base_id
        self.vertices.add(src)
        self.vertices.add(dest)
        self.edges.add(f"{src} {dest}")
        self.edges.add(f"{dest} {src}")

    def next_sample(self):
        self.prev_vertices = get_num_vertices
        self.base_id += total_vertices

    def write_to_file(self):
        diff_e = self.edges - self.edges_in_file
        diff_v = self.vertices - self.vert_in_file

        with open(out_e, 'a') as f:
            for e in diff_e:
                f.write(f"{e}\n")

        with open(out_v, 'a') as f:
            for v in diff_v:
                f.write(f"{v}\n")

        self.vert_in_file += diff_v
        self.edges_in_file += diff_e
