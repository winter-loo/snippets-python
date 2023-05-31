#
# select only function name from gdb stack output
#
# how to generate `gdb.txt`:
#   (gdb) set filename-display absolute
#   (gdb) set logging enabled on
#   (gdb) bt
#   (gdb) set logging enabled off
#
import argparse


class Args(object):
    args = None


def filter_gdb_frame(frame):
    # print('>>>>frame start>>>>')
    # print(frame.strip())
    # print('<<<<frame end<<<<')

    idx = frame.find(' (')
    funcname = frame[:idx].split(' ')[-1]

    idx = frame.find('at ')
    if idx != -1:
        filename, lino = frame[idx + 3:].split(':')
        if Args.args.path_prefix_to_remove is not None:
            if filename.startswith(Args.args.path_prefix_to_remove):
                startpos = len(Args.args.path_prefix_to_remove)
                if not Args.args.path_prefix_to_remove.endswith('/'):
                    startpos += 1
                filename = filename[startpos:]

    if Args.args.with_loc:
        print(f"{funcname} {filename}:{lino}")
    else:
        print(f"{funcname}")


def main():
    with open(Args.args.gdb_logging_file) as f:
        in_stack = False

        while True:
            buf = f.read()
            if len(buf) == 0:
                break
            left = 0
            r = 0

            while r < len(buf):
                if buf[r] == '#' and r + 1 < len(buf) and buf[r + 1] == '0':
                    left = r
                    in_stack = True
                elif in_stack and r > 0 and buf[r - 1] == '\n' and (
                        buf[r] != '#' and buf[r] != ' '):
                    in_stack = False
                    frame = buf[left:r - 1]
                    filter_gdb_frame(frame)
                    print("----STACK FRAME DONE----")

                if in_stack and (left < r and r > 0 and buf[r - 1] == '\n'
                                 and buf[r] == '#'):
                    frame = buf[left:r - 1]
                    left = r
                    filter_gdb_frame(frame)
                r += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='print gdb stack frames')

    parser.add_argument('--with-loc',
                        '-l',
                        action='store_true',
                        help='print with location')
    parser.add_argument('--gdb-logging-file',
                        '-f',
                        default='gdb.txt',
                        help='gdb logging file')
    parser.add_argument('--path-prefix-to-remove',
                        '-p',
                        help='remove directory prefix from filename')

    Args.args = parser.parse_args()

    main()
