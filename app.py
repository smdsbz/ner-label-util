# -*- coding: utf-8 -*-

import curses
from window import Window
from dataloader import JsonDataloader

import sys

src = ''
dump = ''
if len(sys.argv) == 1:
    print('Usage: python3 app.py DUMP_FILE [SRC_FILE]')
else:
    dump = sys.argv[1]
if len(sys.argv) == 3:
    src = sys.argv[2]

dataloader = JsonDataloader(src=src, dump=dump)

if __name__ == '__main__':
    curses.wrapper(Window, dataloader=dataloader)