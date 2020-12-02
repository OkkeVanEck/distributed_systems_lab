import sys


file = sys.argv[1]
with open(file, 'r+') as f:
    all_vertexes = {}
    ends = []
    for line in f.readlines():
        if line[0] == '[':
            vertexes = line.split()
            vertexes[0] = vertexes[0][1:-1]
            vertexes[1] = vertexes[1][:-1]
            if vertexes[0] in all_vertexes:
                all_vertexes[vertexes[0]].append(vertexes[1])
            else:
                all_vertexes[vertexes[0]] = [vertexes[1]]

    keys_not_in_edges = []
    for key in list(all_vertexes.keys()):
        key_found = False
        for key_2 in list(all_vertexes.keys()):
            if key == key_2:
                continue
            if key in all_vertexes[key_2]:
                key_found = True
                break
        if not key_found:
            keys_not_in_edges.append(key)

    print(keys_not_in_edges)
    print("amount of nodes = " + str(len(all_vertexes.keys())))



