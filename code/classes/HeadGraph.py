import logging
from TimeIt import timeit

func_to_time = ["edges2file", "write2file"]
timer = {func:0 for func in func_to_time}
counter = {func:0 for func in func_to_time}

class HeadGraph:
    def __init__(self, total_vertices, num_sample, out_e, out_v):
        """
        Graphs class used by the HeadNode, to keep track of resulting graph.

        total_vertices: number of vertices in the original graph
        num_sample: number of samples that it needs to track
        out_e: output file for the edges
        out_v: output file for the vertices
        """
        self.base_id = 0
        self.total_vertices = total_vertices;
        self.vertices = [set() for _ in range(num_sample)]
        self.edges = set()
        self.out_e = out_e
        self.out_v = out_v
        with open(self.out_e, 'w') as f:
            pass
        with open(self.out_v, 'w') as f:
            pass

    def __del__(self):
        for k, v in timer.items():
            logging.info(f"timer {k} {v:.2f}")

        for k, v in counter.items():
            logging.info(f"counter {k} {v}")

    def get_num_sample_vertices(self, sample):
        return len(self.vertices[sample])

    def get_vertices(self):
        return self.vertices

    def get_vertices_as_one(self):
        """Returns the vertices as a single set."""
        return set().union(*(self.vertices))

    def add_edge(self, vertex_from, vertex_to, sample, base_id=None):
        """
        Adds the 2 given vertices into the graph in the correct sample, and adds
        them as an 2 edges (both from to and to from) in the graph.

        vertex_from: 1 of the vertices in the edge.
        vertex_to: other vertices in the edge. order is abritrary since edge
                   is added both ways
        sample: sample vertices belong too
        base_id: value to be added to the vertices so when upscaling no nodes
                 are considered dublicates. if unchange defaults to the correct
                 id for the current sample
        """
        if base_id == None:
            base_id = self.base_id
        src = vertex_from + base_id
        dest = vertex_to + base_id
        if sample != None:
            self.vertices[sample].add(src)
            self.vertices[sample].add(dest)
        self.edges.add(f"{src} {dest}")
        self.edges.add(f"{dest} {src}")

    def next_sample(self):
        """
        moves the graph to the next sample, needed for counting up the base id
        and printing the edges to the file and clearing it to safe memory.
        """
        self.base_id += self.total_vertices
        self.edges2file()
        self.edges = set()

    @timeit(timer=timer, counter=counter)
    def edges2file(self):
        """prints the edges to the out_e."""
        with open(self.out_e, 'a') as f:
            for e in self.edges:
                f.write(f"{e}\n")

    @timeit(timer=timer, counter=counter)
    def write2file(self):
        """prints vertices and edges to their corresponding output files."""
        with open(self.out_e, 'a') as f:
            for e in self.edges:
                f.write(f"{e}\n")

        with open(self.out_v, 'a') as f:
            for sample in self.vertices:
                for v in sample:
                    f.write(f"{v}\n")
