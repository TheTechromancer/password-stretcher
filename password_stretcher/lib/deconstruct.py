#!/usr/bin/env python3

# by TheTechromancer

import re
from .mutator import Mutator


class Deconstruct(Mutator):

    word_regexes = [re.compile(r, re.I) for r in [
        rb'\w+',
        rb'[0-9]+',
        rb'[\w0-9]+',
        rb'[a-z]+',
        rb'[a-z0-9]+',
        rb'[a-z-]+',
        rb'[a-z0-9-]+'
    ]]

    def __init__(self, _input, limit=256):

        super().__init__(_input, limit)


    def mutate(self, word):

        yield word
        for r in self.word_regexes:
            for m in r.findall(word):
                yield m
