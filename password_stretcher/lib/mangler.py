#!/usr/bin/env python3

# by TheTechromancer

from .cap import Cap
from .leet import Leet
from .pend import Pend
from .perm import Perm
from functools import reduce

class Mangler():

    def __init__(self, _input, output_size=None, double=False, perm=0, leet=False, cap=False, capswap=False, pend=False, key=lambda x: x):

        # load input list into memory and deduplicate
        if cap and not capswap:
            self.input = set(Cap(_input))
        else:
            self.input = set(_input)

        self.input = list(self.input)
        self.input.sort(key=lambda x: len(x))

        self.perm_depth = perm
        self.leet       = leet
        self.capswap    = capswap
        self.cap        = cap or capswap
        self.double     = double
        self.pend       = pend

        self.mutators = [Perm(self.input, double=double, perm_depth=perm)]

        if self.leet:
            self.mutators.append(Leet(self.mutators[-1]))
        if self.capswap:
            self.mutators.append(Cap(self.mutators[-1], capswap=True))
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

        for m in self.mutators:
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



    def set_output_size(self, target_size):
        '''
        sets self.max_cap and self.max_leet based on desired output size

        (s1*m) * (s2*m) * (s3*m) = t
        where each () is a mutator
        t = targe size (known)
        m = multiplier (unknown)
        s = mutator's scale (known)
        solving for m
        '''

        self.output_size = target_size

        x = target_size / len(self.mutators[0])
        num_mutators = len(self.mutators[1:])

        # multiply scales together
        try:
            cumulative_scale = reduce(lambda x, y: x*y, [m.scale for m in self.mutators[1:]])
        except TypeError:
            cumulative_scale = 1

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