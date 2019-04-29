# -*- coding: utf-8 -*-

import curses

import locale
locale.setlocale(locale.LC_ALL, '')

# a to z, A to Z, -, _
label_chars = (
    [chr(o) for o in range(ord('a'), ord('z') + 1)]
    + [chr(o) for o in range(ord('A'), ord('Z') + 1)]
    + list('_-')
)

# init color pairs
COLOR_MODES = {
    name: index + 1
    for index, name in enumerate([
        # 'normal',
        'statusbar_normal',
        'statusbar_insert',
        'statusbar_warning',
        'headerbar',
    ])
}


class Window:
    '''TUI Window Manager Class'''

    MODES = [
        'normal',
        'insert',
    ]

    def __init__(self, stdscr, *args, **kwargs):
        # attach to screen
        self._stdscr = stdscr
        # register dataloader
        self._dataloader = None
        if 'dataloader' in kwargs:
            self._dataloader = kwargs['dataloader']
        # create color profile
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_MODES['statusbar_normal'],
                curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(COLOR_MODES['statusbar_insert'],
                curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(COLOR_MODES['statusbar_warning'],
                curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(COLOR_MODES['headerbar'],
                curses.COLOR_BLACK, curses.COLOR_WHITE)
        # initialize program state
        self._mode = 'normal'
        self._lastkey = None
        self._insert_buffer = ''
        self._warning_text = None
        # start event loop
        self.event_loop()

    def event_loop(self):
        self._stdscr.clear()
        self._stdscr.refresh()
        while True:
            assert self._mode in Window.MODES
            self._stdscr.clear()

            if self._handle_key() is False:
                self._dataloader.save()
                return

            height, width = self._stdscr.getmaxyx()
            self._describe_statusbar(width, height)
            self._describe_trunk(width, height)

            self._stdscr.refresh()
            self._lastkey = self._stdscr.getch()

        # quitting this app
        self._dataloader.save()
        return

    def _handle_key(self) -> bool:
        if self._mode == 'normal':
            if self._lastkey in [curses.KEY_UP, ord('k')]:      # previous char
                try:
                    self._dataloader.cursor_char -= 1
                except IndexError:
                    self._warning_text = 'First char in sentence!'
            elif self._lastkey in [curses.KEY_DOWN, ord('j')]:  # next char
                try:
                    self._dataloader.cursor_char += 1
                except IndexError:
                    self._warning_text = 'Last char in sentence!'
            elif self._lastkey in [curses.KEY_LEFT, ord('h')]:  # previous sentence
                try:
                    self._dataloader.cursor_line -= 1
                    self._dataloader.cursor_char = 0
                except IndexError:
                    self._warning_text = 'First sentence in corpus!'
            elif self._lastkey in [curses.KEY_RIGHT, ord('l')]: # next sentence
                try:
                    self._dataloader.cursor_line += 1
                    self._dataloader.cursor_char = 0
                except IndexError:
                    self._warning_text = 'Last sentence in corpus!'
            elif self._lastkey in list(map(ord, 'Ib')):         # tagging 'begin', to insert mode
                self._mode = 'insert'
            elif self._lastkey == ord('i'):                     # tag 'within'
                char = self._dataloader.cursor_char
                if char == 0:
                    self._warning_text = "The 'within' tag cannot be the first tag!"
                else:
                    last_label = self._dataloader.get_char_label(char=char-1)[1]
                    if last_label is None or last_label[0] not in 'BI':
                        self._warning_text = "The 'within' tag must follow 'begin' or a previous 'within'!"
                    else:
                        self._dataloader.label_char('I')
            elif self._lastkey == ord('o'):                     # tag 'out-of'
                self._dataloader.label_char('O')
            elif self._lastkey in list(map(ord, 'qQ')):         # quit
                return False
        elif self._mode == 'insert':
            if self._lastkey in [curses.KEY_ENTER, ord('\n')]:
                self._mode = 'normal'
                self._dataloader.label_char('B-{}'.format(self._insert_buffer))
                self._insert_buffer = ''
            elif chr(self._lastkey) in label_chars:             # legal alphas
                self._insert_buffer += chr(self._lastkey)
        return True

    def _describe_statusbar(self, width: int, height: int):
        '''Refreshed status bar.'''
        assert self._mode in Window.MODES
        if self._warning_text is not None:
            self._describe_warning_statusbar(width, height, self._warning_text)
            self._warning_text = None
        elif self._mode == 'normal':
            self._describe_normal_statusbar(width, height)
        elif self._mode == 'insert':
            self._describe_insert_statusbar(width, height)
        else:
            raise NotImplementedError("Mode '{}' not implemented!".format(self._mode))

    def _describe_warning_statusbar(self, width: int, height: int, msg: str):
        self._stdscr.attron(curses.color_pair(COLOR_MODES['statusbar_warning']))
        self._stdscr.addstr(height - 1, 0, (msg + ' ' * width)[:width-1])
        self._stdscr.attroff(curses.color_pair(COLOR_MODES['statusbar_warning']))

    def _describe_normal_statusbar(self, width: int, height: int):
        self._stdscr.attron(curses.color_pair(COLOR_MODES['statusbar_normal']))
        self._stdscr.addstr(height - 1, 0, (
            "q - save and quit | w - save | j/k - next/prev char | b - begin | i - within | o - out-of"
            + ' ' * width)[:width-1]
        )
        self._stdscr.attroff(curses.color_pair(COLOR_MODES['statusbar_normal']))

    def _describe_insert_statusbar(self, width: int, height: int):
        self._stdscr.attron(curses.color_pair(COLOR_MODES['statusbar_insert']))
        self._stdscr.addstr(height - 1, 0,
            ('LABEL  B-{}'.format(self._insert_buffer) + ' ' * width)[:width-1]
        )
        self._stdscr.attroff(curses.color_pair(COLOR_MODES['statusbar_insert']))

    def _describe_trunk(self, width: int, height: int):
        '''Refreshes trunk display.'''
        self._describe_text_area(width=width, height=height)

    def _describe_text_area(self, width: int, height: int,
            margin: int=9, padding: int=5):
        '''Refreshes text display.'''
        assert margin >= 2
        center_idx = self._dataloader.cursor_char
        in_range = lambda idx: idx >= 0 and idx < len(self._dataloader.current_line)
        content = {
            idx: (
                self._dataloader.get_char_label(char=idx)
                if in_range(idx) else None
            ) for idx in range(center_idx - margin, center_idx + margin + 1)
        }
        cur_x_mid = width // 2
        for idx, cont in content.items():
            if cont is None:
                continue
            offset = idx - center_idx
            cur_y = height // 2 + offset * 2
            self._stdscr.addstr(cur_y, cur_x_mid - 2, cont[0])
            self._stdscr.addstr(cur_y, cur_x_mid + 2, cont[1] or '_')
        self._stdscr.move(height // 2, cur_x_mid + 2)
