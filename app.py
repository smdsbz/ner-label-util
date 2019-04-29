# -*- coding: utf-8 -*-

import curses
from window import Window
from dataloader import DevDataloader

dataloader = DevDataloader()

if __name__ == '__main__':
    curses.wrapper(Window, dataloader=dataloader)