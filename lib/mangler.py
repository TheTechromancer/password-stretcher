#!/usr/bin/env python3

# by TheTechromancer

import itertools


class Mangler():

    def __init__(self, in_list, double=0, perm=0, leet=False, cap=False, capswap=False, key=lambda x: x):

        # "leet" character swaps - modify as needed.
        # Keys are replaceable characters; values are their leet replacements.

        self.leet_common = self._dict_str_to_bytes({
            'a': ['@'],
            'A': ['@'],
            'e': ['3'],
            'E': ['3'],
            'i': ['1'],
            'I': ['1'],
            'o': ['0'],
            'O': ['0'],
            's': ['$'],
            'S': ['$'],
        })

        self.leet_all = self._dict_str_to_bytes({
            'a': ['4', '@'],
            'A': ['4', '@'],
            'b': ['8'],
            'B': ['8'],
            'e': ['3'],
            'E': ['3'],
            'i': ['1'],
            'I': ['1'],
            'l': ['1'],
            'L': ['1'],
            'o': ['0'],
            'O': ['0'],
            's': ['5', '$'],
            'S': ['5', '$'],
            't': ['7'],
            'T': ['7']
        })

        self.in_list        = in_list

        # max_* = maximum mutations per word
        # cur_* = used for carrying over unused mutations into next iteration
        self.max_leet       = 128 # max number of leet mutations per word
        self.max_cap        = 256 # max number of capitalization mutations per word
        self.cur_leet       = 0
        self.cur_cap        = 0

        self.perm_depth     = perm
        self.do_leet        = leet
        self.do_capswap     = capswap
        self.do_cap         = cap or capswap
        self.double         = double

        self.key            = key



    def __iter__(self):
        '''
        generator function
        runs mangling functions on wordlist
        yields each mutated word
        '''

        for word in self.cap(self.leet(self.perm())):
            yield word


    def perm(self):
        '''
        permutates words from iterable
        takes:      iterable containing words
        yields:     word permutations ('pass', 'word' --> 'password', 'wordpass', etc.)
        '''

        if self.perm_depth > 1:

            words = [ self.key(w) for w in self.in_list ]

            for d in range(1, self.perm_depth+1):
                for p in itertools.product(words, repeat=d):
                    yield b''.join(p)

        else:
            for word in self.in_list:

                word = self.key(word)

                yield word

                if self.double:
                    yield word + word



    def cap(self, in_list):

        for word in in_list:

            if self.do_cap:

                self.cur_cap += self.max_cap

                for r in self._cap(word):
                    self.cur_cap -= 1
                    yield r
                    if self.cur_cap <= 0:
                        break

            else:
                yield word



    def leet(self, in_list):

        for word in in_list:

            gen_common = self._leet(word, swap_values=self.leet_all)
            yield next(gen_common)

            if self.do_leet:

                self.cur_leet += self.max_leet
                num_results = 0

                for r in gen_common:
                    self.cur_leet -= 1
                    if self.cur_leet <= 0:
                        break
                    yield r



    def _leet(self, word, swap_values=None):

        if not swap_values:
            swap_values = self.leet_all

        if len(word) == 1:
            yield word
            try:
                for leet_char in swap_values[word]:
                    yield leet_char
            except KeyError:
                pass

        else:
            mid_point = int(len(word)/2)
            for right_half in self._leet(word[mid_point:], swap_values=swap_values):
                for left_half in self._leet(word[:mid_point], swap_values=swap_values):
                    yield left_half + right_half




    def _cap(self, word):


        # always yield the most likely candidates first
        results = []
        for r in [word, word.lower(), word.upper(), word.swapcase(), word.capitalize(), word.title()]:
            if r not in results:
                results.append(r)
                yield r

        # then move on to full cap mutations if requested
        if self.do_capswap:
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





    def _dict_str_to_bytes(self, d):

        new_dict = {}
        for key in d:
            new_dict[key.encode('utf-8')] = [v.encode('utf-8') for v in d[key]]
        return new_dict



    def _le3t(self, word, swap_values=None):
        '''
        takes:      iterable containing words
                    swap_values: dictionary containing leet swaps
                    passthrough: whether or not to yield unmodified word
        yields:     leet mutations, not exceeding max_results per word
        '''

        if not swap_values:
            swap_values = self.leet_all

        swaps = []
        word_length = len(word)

        for i in range(word_length):
            try:
                for l in swap_values[word[i]]:
                    swaps.append((i, l))

            except KeyError:
                continue

        num_swaps_range = range(len(swaps))
        word_list = list(word)


        for num_swaps in num_swaps_range:

            for c in itertools.combinations(num_swaps_range, num_swaps+1):

                try:

                    new_word = word_list.copy()
                    already_swapped = []

                    for n in c:
                        assert not swaps[n][0] in already_swapped
                        new_word[swaps[n][0]] = swaps[n][1]
                        already_swapped.append(swaps[n][0])

                    yield bytes(new_word)

                except AssertionError:
                    continue