#
# select only function name from gdb stack output
#
# how to generate `gdb.txt`:
#   (gdb) set logging on
#   (gdb) bt
#   (gdb) set logging off
#
with open('gdb.txt') as gdb_stack:
    firstLine = True
    offset = 2
    for line in gdb_stack:
        if not line.startswith('#') or len(line) == 0:
            continue
        tokens = line.strip().split(' ')

        if firstLine:
            firstLine = False
            offset = 0
        else:
            offset = 2

        i = 1
        while len(tokens[i]) == 0:
            i += 1
        funcname = tokens[i + offset]
        print(funcname)
