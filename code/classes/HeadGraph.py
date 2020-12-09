

class HeadGraph:
    def __init__(self, total_vertices, num_sample, out_e, out_v):
        self.base_id = 0
        self.total_vertices = total_vertices;
        self.vertices = [set()] * num_sample
        self.current_sample = 0;
        self.edges = set()
        self.out_e = out_e
        self.out_v = out_v

    def get_num_sample_vertices(self):
        return len(self.vertices[self.current_sample])

    def get_vertices(self):
        return self.vertices

    def add_edge(self, vertex_from, vertex_to, sample, base_id=None):
        if base_id == None:
            base_id = self.base_id
        src = vertex_from + base_id
        dest = vertex_to + base_id
        if sample != None:
            self.vertices[self.current_sample].add(src)
            self.vertices[self.current_sample].add(dest)
        self.edges.add(f"{src} {dest}")
        self.edges.add(f"{dest} {src}")

    def next_sample(self):
        self.current_sample += 1
        self.base_id += self.total_vertices

    def write2file(self):
        with open(self.out_e, 'a') as f:
            for e in self.edges:
                f.write(f"{e}\n")

        with open(self.out_v, 'a') as f:
            for sample in vertices:
                for v in sample:
                    f.write(f"{v}\n")
