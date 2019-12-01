#!/usr/bin/env python3

# by TheTechromancer

import itertools
from .cap import Cap
from .leet import Leet
from .pend import Pend
from functools import reduce

class Mangler():

    def __init__(self, _input, output_size=None, double=0, perm=0, leet=False, cap=False, capswap=False, pend=False, key=lambda x: x):

        total_words     = 0
        total_word_size = 0

        # load input list into memory and deduplicate
        self.input = set()
        for word in _input:
            total_words += 1
            total_word_size += len(word)
            self.input.add(key(word))
        self.input = list(self.input)
        self.input.sort(key=lambda x: len(x))

        self.perm_depth = perm
        self.leet       = leet
        self.capswap    = capswap
        self.cap        = cap or capswap
        self.double     = double
        self.pend       = pend

        self.mutators = [self.perm()]

        if self.leet:
            self.mutators.append(Leet(self.mutators[-1]))
        if self.cap:
            self.mutators.append(Cap(self.mutators[-1], capswap=self.capswap))
        if self.pend:
            self.mutators.append(Pend(self.mutators[-1]))

        if output_size:
            self.set_output_size(output_size)
        else:
            self.set_output_size(max(len(self.input)*1000, 100000000))


    def __iter__(self):
        '''
        generator function
        runs mangling functions on wordlist
        yields each mutated word
        '''

        for word in self.mutators[-1]:
            yield word


    def __len__(self):
        '''
        Estimates the total output length based on requested mangling parameters
        '''

        length = int(self.input_length)

        for m in self.mutators[1:]:
            length *= len(m)

        return int(length)


    def chain_mutators(self, _input=None, mutators=None):

        if mutators is None:
            mutators = self.mutators
        if _input is None:
            _input = self.perm()

        if len(mutators) == 0:
            return _input

        return self.chain_mutators(mutators[0].gen(_input), mutators[1:])


    def perm(self):
        '''
        permutates words from iterable
        takes:      iterable containing words
        yields:     word permutations ('pass', 'word' --> 'password', 'wordpass', etc.)
        '''

        if self.perm_depth > 1:
            for d in range(1, self.perm_depth+1):
                for p in itertools.product(self.input, repeat=d):
                    yield b''.join(p)

        else:
            for word in self.input:

                yield word

                if self.double:
                    yield word + word





    def set_output_size(self, target_size):
        '''
        sets self.max_cap and self.max_leet based on desired output size

        x * 2x * 5x = target_size
        '''

        self.output_size = target_size

        x = target_size / self.input_length
        num_mutators = len(self.mutators[1:])

        # multiply scales together
        cumulative_scale = reduce(lambda x, y: x*y, [m.scale for m in self.mutators[1:]])

        if self.cap and not self.capswap:
            x = int(x / Cap.cap_multiplier)
        try:
            x = x / cumulative_scale
        except ArithmeticError:
            pass

        try:
            x **= (1 / num_mutators)
            for mutator in self.mutators[1:]:
                mutator.limit = max(1, int(x * mutator.scale))
        except ArithmeticError:
            pass

        '''
        if self.capswap and self.leet:
            multiplier = (multiplier / 2) ** (1 / 2)
            self.max_cap = max(1, int(multiplier * 2))
            self.max_leet = max(1, int(multiplier))

        elif self.cap and self.leet:
            self.max_leet = int(multiplier / Cap.cap_multiplier)

        elif self.capswap:
            self.max_cap = max(1, int(multiplier))

        elif self.leet:
            self.max_leet = max(1, int(multiplier))
        '''


    @property
    def input_length(self):

        length = len(self.input)

        if self.perm_depth > 1:
            initial_length = len(self.input)
            for i in range(2, self.perm_depth+1):
                length += initial_length ** i

        elif self.double:
            length *= 2

        # prevent division by zero
        return max(1, length)