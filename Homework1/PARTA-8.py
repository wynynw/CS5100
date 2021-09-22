
graph = {
    '0': ['1', '4'],
    '1': ['2', '3'],
    '2': ['1'],
    '3': ['1'],
    '4': ['5', '6'],
    '5': ['4'],
    '6': ['4'],
}

def BFS(graph, s):
    queue = []
    queue.append(s)
    seen = set()
    seen.add(s)
    parent = {s: None}
    while len(queue) > 0:
        vertex = queue.pop(0)
        nodes = graph[vertex]
        for w in nodes:
            if w not in seen:
                queue.append(w)
                seen.add(w)
                parent[w] = vertex
        print(vertex)
    return parent

def DFS(graph, s):
    stack = []
    stack.append(s)
    seen = set()
    seen.add(s)
    parent = {s: None}
    while len(stack) > 0:
        vertex = stack.pop()
        nodes = graph[vertex]
        for w in nodes:
            if w not in seen:
                stack.append(w)
                seen.add(w)
                parent[w] = vertex
        print(vertex)
    return parent

parent = BFS(graph, '0')
for key in parent:
	print(key, parent[key])

parent1 = DFS(graph, '0')
for key in parent1:
	print(key, parent[key])


