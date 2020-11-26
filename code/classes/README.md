# Classes
Classes contains _.py_ files which each define a data structure.

### Naming conventions
TODO


### TODO
- [ ] Make a head node class, responsible for stitching, listening for heartbeats, writing resulting graph to file
- [ ] Implement MPI comminication in head node class, compute node class
- - [ ] heartbeats
- - [ ] fire spread communication between compute nodes
- - [ ] Allow Compute Node to have multiple partitions assigned, with each partition owning a fire.
- - - When a fire spreads a compute node should first check local partitions.
- [ ] Implement a way to run the script with halted forest fires vs wild fires
- [ ] determine clustered partitions of input graphs
- [ ] write script to do graph analysis using the snap library
