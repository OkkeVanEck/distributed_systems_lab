from Graph import Graph
from Vertex import Vertex
from Enums import *


def get_new_unburned_vertex(i):
    return Vertex(i, VertexStatus.NOT_BURNED)



def get_vertexes(G, list_v):
    ret = []
    for v in G.graph:
        if v.vertex_id in list_v:
            ret.append(v)
    return ret


def test_graph_set_vertex_status():
    # no compute node
    G = Graph(None)
    G.add_vertex_and_neighbor(0, 1)
    G.add_vertex_and_neighbor(1, 0)
    G.add_vertex_and_neighbor(0, 2)
    G.add_vertex_and_neighbor(2, 0)
    [v0, v1, v2] = get_vertexes(G, [0, 1, 2])
    G.set_vertex_status(v1, v0, VertexStatus.BURNED)
    if G.get_vertex_status(v0) != VertexStatus.BURNED:
        print("0 vertex key was not burned")
        return False
    if G.get_vertex_status(v1) != VertexStatus.BURNED:
        print("1 vertex key was not burned")
        return False
    for v in G.graph[v0]:
        if v.vertex_id == 1:
            if v.status != VertexStatus.BURNED:
                print("vertex 1 (neighbor of 0) was not burned")
                return False
    for v in G.graph[v1]:
        if v.vertex_id == 0:
            if v.status != VertexStatus.BURNED:
                print("vertex 0 (neighbor of 1) was not burned")
                return False
    return True


print(test_graph_set_vertex_status())