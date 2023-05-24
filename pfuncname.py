#
# select only function name from gdb stack output
#
# how to generate `gdb.txt`:
#   (gdb) set logging on
#   (gdb) bt
#   (gdb) set logging off
#
import os
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
    filename = filename.split(os.sep)[-1]

  if Args.args.with_loc == True:
    print(f"{funcname} {filename}:{lino}")
  else:
    print(f"{funcname}")


def main():
  with open('gdb.txt') as f:
      in_stack = False
  
      while True:
        buf = f.read()
        if len(buf) == 0:
          break
        l = 0
        r = 0
  
        while r < len(buf):
          if buf[r] == '#' and r + 1 < len(buf) and buf[r + 1] == '0':
            l = r
            in_stack = True
          elif in_stack and r > 0 and buf[r - 1] == '\n' and (buf[r] != '#' and buf[r] != ' '):
            in_stack = False
            frame = buf[l:r-1]
            filter_gdb_frame(frame)
            print("----STACK FRAME DONE----")
  
          if in_stack and (l < r and r > 0 and buf[r - 1] == '\n' and buf[r] == '#'):
            frame = buf[l:r-1]
            l = r
            filter_gdb_frame(frame)
          r += 1

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='print gdb stack frames')

  parser.add_argument('--with-loc', '-l', action='store_true', help='print with location')

  Args.args = parser.parse_args()

  main()
