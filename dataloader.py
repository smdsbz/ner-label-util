# -*- coding: utf-8 -*-

from typing import Tuple, Union

import json


class BaseDataloader:
    def __init__(self, src: str, dump: str, use_generator: bool=False):
        with open(src, 'r') as f:
            self._raw_text = json.load(f)
        pass

class DevDataloader:
    def __init__(self, dump: str='testdump.json'):
        self._raw_text = [
            '由于谐振，故所有电抗之和等于零：）'
        ]
        self._labels = [
            [None for ch in line]
            for line in self._raw_text
        ]
        self.dump_path = dump
        self._cur = [0, 0]

    def save(self, path: str=None):
        with open(path or self.dump_path, 'w') as f:
            json.dump([
                {
                    'raw': raw,
                    'lab': label
                } for raw, label in zip(self._raw_text, self._labels)
            ], f)

    @property
    def cursor_line(self) -> int:
        '''Cursor line index'''
        return self._cur[0]

    @cursor_line.setter
    def cursor_line(self, val: int):
        if val < 0 or val > len(self._raw_text):
            raise IndexError()
        self._cur[0] = val

    @property
    def cursor_char(self) -> int:
        '''Cursor char index in current line'''
        return self._cur[1]

    @cursor_char.setter
    def cursor_char(self, val: int):
        if val < 0 or val >= len(self._raw_text[self._cur[0]]):
            raise IndexError()
        self._cur[1] = val

    @property
    def current_line(self) -> str:
        return self._raw_text[self.cursor_line]

    def has_reached_end(self):
        return self.cursor_line >= len(self._raw_text)

    def get_char_label(self, line: int=None, char: int=None) -> Union[Tuple[str, str], None]:
        line = line if line is not None else self.cursor_line
        char = char if char is not None else self.cursor_char
        if line >= len(self._raw_text):
            return None
        if char >= len(self._raw_text[line]):
            return None
        return (self._raw_text[line][char], self._labels[line][char])

    def label_char(self, label: str, assert_current_char: str=None) -> bool:
        '''Labels the current character.

        Args:
            label: The label
            assert_current_char: Used for current char assertion (default: None)

        Returns:
            A boolean whether the current line has finished.
        '''
        assert assert_current_char is None                                  \
            or assert_current_char == self._raw_text[self.cursor_line][self.cursor_char]
        self._labels[self.cursor_line][self.cursor_char] = label
        try:
            self.cursor_char += 1
        except IndexError:
            self.cursor_char = 0
            try:
                self.cursor_line += 1
            except IndexError:
                return False
        return True
