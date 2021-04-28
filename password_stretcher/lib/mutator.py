#!/usr/bin/env python3

# by TheTechromancer


class Mutator():
    '''
    base class for mutators like capswap, leet, and *pend
    '''

    # prioritization compared to other mutators when limit is being enforced
    # e.g. "pend" gets a scale of 5 while "leet" gets 1
    # this means that for every 1 leet mutation, there are 5 pend mutations
    scale = 1
    # friendly name to describe mutator type
    fname = 'mutator'

    def __init__(self, _input, limit=128):

        self.input = _input

        # maximum mutations per word
        self.limit = limit
        # carry over unused mutations into the next word
        self.cur_limit = 0


    def __len__(self):

        return self.limit


    def __iter__(self):

        for word in self.input:
            self.cur_limit += self.limit
            for r in self.mutate(word):
                if self.cur_limit > 0:
                    yield r
                    self.cur_limit -= 1
                else:
                    break


    def __str__(self):

        return self.fname


    def mutate(self, word):
        '''
        override in child class
        '''
        yield word