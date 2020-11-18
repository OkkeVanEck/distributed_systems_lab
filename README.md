# Distributed Systems Lab


### Code Design
#### Classe design + explaination.
See code_design for more details.

```
one instance is present on every node. The Compute node is
responsible for keeping track of the fires on the node
This means starting fires, and making sure no fire burns the same
node.
class Compute_node:

The fire represents the sampled graph.
There is a vertex threshold that each fire instance needs to reach, 
and once the vertex threshold is reached, the sampled graph is 
returned to the head node for stitching.
Burned vertexes in a fire also have what will be known as a burn 
step. This is a representation of what time step a vertex joined the 
fire.
If the fire spreads to other nodes, the other nodes start another 
fire at the border vertex with the appropriate burn step passed in 
the message.
When the fire needs to be collected, each fire collects itself from 
the nodes it spread to and trims itself by choosing the first X 
vertexes with the lowest burn step.
class Fire:

Graph representation. Used by compute nodes and by Fires to maintain 
the sampled graph
class Graph:

vertex class used by the fire. Includes a burn_step
class b_vertex:
```

#### Handling communication of burns across compute nodes
When a forest fire f burning on compute node i burns into vertex v which is assigned to node j, the following happens;
- Node i sends a message to node j that a new fire needs to start at vertex v. The message contains the following information
    1. The node path of fire f. This means where the fire started, and what other compute nodes the fire has already traveled to (this information is stored by the fire)
    2. The burn step of the fire. Every fire has a burn step representing what iteration of burning the fire is currently on. Every vertex burned stores its burn step
    3. The maximum number of vertexes the fire on node j can burn before stopping. The fire on node i keeps this information up to date after every burn step. Because the fire knows how many vertexes it needs to burn total, it can know how many vertexes a fire starting on another node needs to burn maximum.
    4. The fire_id. When the fire is collected, the fire_id is used to determine what fires to collect.
#### How to return burns to compute nodes when they are finished.
When a fire f is done burning on node i there are two possibilities, and from there two paths of computation
1. The fire hasn’t spread to any other compute nodes. In this case,
    - return the sampled fire graph to whatever node requested you to burn.
2. The fire has burned to other compute nodes. In this case,
    - Request a collection of fires from the nodes the fire has spread to.
While gathering the fires, merge them into the current fire
Since the Fire has a vertex_threshold, merging means maintaining the threshold, and preferring vertexes with lower burn_steps.
    - Return the merged fire to whatever node requested the fire to burn.

#### If a fire is requested to be collected.
- Stop the burning process and simulate the done burning step above.