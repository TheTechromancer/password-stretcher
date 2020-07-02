#!/usr/bin/env python3

# by TheTechromancer

import itertools
from .mutator import Mutator


class Perm(Mutator):
    '''
    permutates words from iterable
    takes:      iterable containing words
    yields:     word permutations ('pass', 'word' --> 'password', 'wordpass', etc.)
    '''

    fname = 'perm'

    def __init__(self, _input, perm_depth=0, double=False):

        self.perm_depth = perm_depth
        self.double = double
        self.input = _input

        super().__init__(_input, limit=None)


    def __len__(self):

        length = len(self.input)

        if self.perm_depth > 1:
            initial_length = len(self.input)
            for i in range(2, self.perm_depth+1):
                length += initial_length ** i

        elif self.double:
            length *= 2

        # prevent division by zero
        return max(1, length)


    def __iter__(self):

        if self.perm_depth > 1:
            for d in range(1, self.perm_depth+1):
                for p in itertools.product(self.input, repeat=d):
                    yield b''.join(p)

        else:
            for word in self.input:
                yield word
                if self.double:
                    yield word + word