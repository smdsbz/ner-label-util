# -*- coding: utf-8 -*-

from typing import List, Tuple, Union

import os
import json


class BaseDataloader:
    '''Dev-use Dataloader

    @src of __init__() is not used.
    '''

    def __init__(self, src: str='not used in dev-mode', dump: str='testdump.json'):
        '''
        Args:
            src: Source file
            dump: Save location

        See also get_raw_text_and_labels().
        '''
        self._raw_text, self._labels = self.get_raw_text_and_labels(src, dump)
        self.dump_path = dump
        self._cur = list(self.first_unlabeled_cursor())

    @staticmethod
    def get_raw_text_and_labels(src: str, dump: str) -> Tuple[List[str], List[Union[None, str]]]:
        '''Creates raw text ingredient and generates phantom labels.

        Args:
            src: Srouce file
            dump: Save location (needed if you want to revive previous data
                from a checkpoint)

        Returns:
            (
                [ 'raw text strings', ...],
                [ ['labels', 'for', 'this', ],
                  ['sentence', 'or', None, ],
                  ['if', 'not', 'yet', 'labeled'] ]
            )

            Label strings may meet the following format:

            - 'B-{category}': Begining of an entity, where '{category}' is the
                category of the entity labeling.
            - 'I': Inside an entity, must follow 'B-{xxx}' or 'I'.
            - 'O': Not part of entities.

        NOTE This should be the ONLY method that's required for re-implementstion
        if you are adapting this utility to your own data.
        '''
        raw_text = [
            '由于谐振，故所有电抗之和等于零：）'
        ]
        labels = [
            [None for ch in line]
            for line in raw_text
        ]
        return (raw_text, labels)

    def first_unlabeled_cursor(self) -> Tuple[int, int]:
        for line_idx, _ in enumerate(self._raw_text):
            for char_idx, label in enumerate(self._labels):
                if label is None:
                    return (line_idx, char_idx)
        return (0, 0)

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
        if val < 0 or val >= len(self._raw_text):
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


class JsonDataloader(BaseDataloader):
    @staticmethod
    def get_raw_text_and_labels(src: str, dump: str) -> Tuple[List[str], List[Union[None, str]]]:
        '''
        If @dump file is present, only load from @dump, @src is ignored.
        Otherwise, load raw text from @src.
        '''
        print('in JsonDataloader.get_raw_text_and_labels()')
        raw_text, labels = [], []
        if os.path.exists(dump):        # load from existing checkpoint
            with open(dump, 'rb') as f:
                for tup in json.load(f):
                    raw_text.append(tup['raw'])
                    labels.append(tup['lab'])
        else:                           # starting from scratch
            # NOTE Here, JSONs are crawed-data in a specific format (ask zrs).
            #   All text fields will be feed into corpus! More is better (cross-fingers)!
            # TODO Tokenize tags <img> et al.
            with open(src, 'rb') as f:  # NOTE 'b' for UTF-8
                for dic in json.load(f):
                    raw_text.extend([
                        dic['question'], dic['questionContent'],
                    ])
                    raw_text.extend(ans_tup[0] for ans_tup in dic['answers'])
            # generate phantom label placeholders
            labels = [
                [None for ch in line] for line in raw_text
            ]
        return (raw_text, labels)