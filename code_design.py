class Compute_node:
    node_id = 0             # node ID 
    node_fire_id = 0        # Fire that belongs to the computational node 
    fires_in_node = []      # list of fires in the node 
    vertices_sampled = {}   # set of sampled vertices within the node.
                            # keeps track of all vertices in the node that have been burned
    edges_sampled = {}      # set of edges sampled in the assigned graph_cut
    vertex_threshold = 0    # number of vertices to sample in sampled graph

    graph_cut = graph()     # A cut of the graph assigned to the node

    # start fire that belongs to the current node
    def init_fire(fire_id, vertex):
        new_fire = Fire(fire_id, vertex)
        add_sampled_vertex(vertex)
        fires_in_node.append(new_fire)
        new_fire.burn()

    # fires_in_node
    def add_sampled_vertex(vertex) :
        vertices_sampled[vertex.v_id] = vertex 

    # fire_id comes from the message sent by other compute node.
    def add_fire_to_node(fire_id, vertex, nodes_spread_to, burn_step, num_nodes_to_burn):
        new_fire = Fire(fire_id, vertex, nodes_spread_to, burn_step, num_nodes_to_burn)
        add_sampled_vertex(vertex)
        fires_in_node.append(new_fire)
        new_fire.burn()

    # get all unburned vertexes for a graph.  
    def get_unburned_neighbors(vertex_id):
        neighbourhood_set = graph_cut.get_neighbours(vertex_id)
        res = {}
        for vertex in neighbourhood_set:
            if vertex not in vertices_sampled:
                res[vertex.v_id] = vertex
        return res


class Fire:
    fire_id = 0                     # int for the fire id
    fire_node_path = []             # list to identify where the fire has spread to
    compute_node = Compute_node()   # compute node the fire is burning on
    sampled_graph = graph()         # graph representing the sampled graph
    burn_step = 0                   # step of the forest fire
    nodes_spread_to = []            # list of nodes the fire has spread to.

    # function to create a fire. Used by a Node to create a fire in
    # every node. Also used to spread fires between nodes.
    def create(vertex):
        # define the current compute node

    def burn();
        while not sampled_graph.reached_max_vertices();
            spread_step()
        collect()
        # return sampled_graph to whatever whoever called for the burn
        # this could be another compute node, or the head node.
        return sampled_graph

    def spread_step():
        for vertex in sampled_graph.vertexes:
            for unburned_vertex in compute_node.get_unburned_neighbors(vertex):
                new_vertex_burned = decide_burn(vertex, unburned_vertex)
                if new_vertex_burned:
                    add_burned_node(vertex, unburned_vertex)
        increment_burn_step()

    def decide_burn(b_vertex, nb_vertex):
        # determine if the burning vertex (b_vertex) burns (nb_vertex)
        # this is where we can decide if we allow communication with other 
        # nodes vertices.

    # tell node with node_id to stop the fire with fire_id and
    # return the sampled_graph collected on the node.
    def collect(fire_id, node_id):
        for node in reversed(nodes_spread_to):
            burned_graph = node.collect(fire_id, node)
            sampled_graph.merge(burned_graph)
        return


    # increment the current number of burned nodes
    def add_burned_node(b_vertex, nb_vertex):
        if # nb_vertex belongs to other node:
            # send message to other node to start a fire at that node
            # if that vertex is already burned in that node, the fire will just stop there
            # send message with something like (fire_id, vertex, nodes_spread_to, burn_step, num_nodes_to_burn) 
            # this is so the node can call add_fire_to_node()
            # update_nodes_spread_t, num_nodes_to_burn)o

        # add the vertex and edge regardless of location of nb_vertex
        sampled_graph.add_vertex_edge(b_vertex, nb_vertex)

    # burn the tree one step, will call add_burned_node
    def increment_burn_step():
        burn_step+=1;


class Graph:
    vertex_to_neighbors = {}        # dict of b_vertex -> list(b_vertex). The list represents

    vertex_count = 0            # number of vertexes in the graph
    max_vertex_count = 0        # max number of vertexes allowed in graph
    last_burn_step = 0          # keep track of last burn step in graph
                                # will help when merging graphs

    def reached_max_vertices():
        return (vertex_count >= max_vertex_count)

    def vertex_in_tree(b_vertex):
        return b_vertex in vertex_to_neighbors

    def add_vertex(b_vertex, nb_vertex, burn_step):
        nb_vertex_new = nb_vertex.copy()
        nb_vertex_new.burn_step = burn_step 
        vertex_to_neighbors[b_vertex].append(nb_vertex_new)
        vertex_count+=1
        # need to add edges of nb_vertex to any burned edges.
        

    def merge(graph_g):
        # merge the two graphs, order merging by burn steps
        # once max_vertex_count is reached, return

    def get_neighbours(b_vertex):
        return vertex_to_neighbors[b_vertex]

# class for burned vertices
class b_vertex:
    v_id = 0        # vertex id
    burn_step = 0   # burn step that the vertex was added to the tree
  