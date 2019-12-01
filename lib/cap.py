#!/usr/bin/env python3

# by TheTechromancer

from .mutator import Mutator


class Cap(Mutator):

    # roughly the number of capital mutations when capswap is disabled
    cap_multiplier = 4
    scale = 2
    fname = 'capitalization'

    def __init__(self, _input, limit=256, capswap=False):

        self.capswap = capswap
        # the average number of words produced by the cap() (not capswap)

        super().__init__(_input, limit)


    def __len__(self):

        if not self.capswap:
            return self.cap_multiplier
        else:
            return self.limit


    def mutate(self, word):

        # always yield the most likely candidates first
        results = []
        for r in [word, word.lower(), word.upper(), word.swapcase(), word.capitalize(), word.title()]:
            if r not in results:
                results.append(r)
                yield r

        # then move on to full cap mutations if requested
        if self.capswap:
            for r in self._capswap(word):
                if not r in results:
                    yield r


    def _capswap(self, word):

         # many recursions make light work
        if len(word) == 1:
            yield word
            if word.isalpha():
                yield word.swapcase()

        else:
            mid_point = int(len(word)/2)
            for right_half in self._capswap(word[mid_point:]):
                for left_half in self._capswap(word[:mid_point]):
                    yield left_half + right_half
