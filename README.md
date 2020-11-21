# Distributed Systems Lab

Basic algorithm procedures:

In each forest fire round, compute nodes
- iterate over the the set of the vertexes to burn, change the status, pick part of its neighbours to burn
- if the neighbour chosen is on the node and not burnt yet
  - add to the vertexes to burn next round or not
  
- if the neighbour chosen is on the other nodes
  - send the id of the vertex to that node
  
- check (or non-blockingly) whether it has received vertex id from other nodes to burn
  - if yes and it's not burnt yet
    - add to the set of the vertexes to burn in its graph

- send the # vertexes to burn next round to the burn to the head node (can be optimised into update in batches)

The head node keep tracks of total #burnt vertexes, once meet the target then bcast all the nodes to stop the fire and gather the burnt vertexes.
