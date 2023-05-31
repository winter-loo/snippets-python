import graphviz

dot = graphviz.Digraph('gdb stack', comment='gdb stack')

relations = dict()

prev_func = None
curr_func = None
with open('funcs.txt') as f:
    for line in f:
        if line.startswith('---'):
            prev_func = None
            continue
        curr_func = line.strip()
        if curr_func not in relations:
            relations[curr_func] = set()

        if prev_func is not None:
            relations[curr_func].add(prev_func)

        prev_func = curr_func

for n in relations.keys():
    dot.node(n)

for n, nns in relations.items():
    if len(nns) == 0:
        continue
    for nn in nns:
        dot.edge(n, nn)

print(dot.source)
