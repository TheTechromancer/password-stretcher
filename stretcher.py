#!/usr/bin/env python3

'''

stretcher.py

by TheTechromancer

TODO:

    Ponder validity of empty rule ( [string] )
    Take out, leave in, or only leave in if len(rules.sorted_rules) == 0?

'''


import itertools
from copy import copy
from time import sleep
from pathlib import Path
from statistics import mean
from functools import reduce
from os import name as os_type
from sys import argv, exit, stdin, stderr, stdout
from argparse import ArgumentParser, FileType, ArgumentError

### DEFAULTS ###

leet_chars      = (b'013578@$') # characters to consider "leet"

max_leet        = 64            # max number of leet mutations per word
max_cap         = 256           # max number of capitalization mutations per word

report_limit    = 50            # maximum lines for each individual report

string_delim    = b'\x00'       # unique unprintable placeholder for strings
digit_delim     = b'\x01'       # unique unprintable placeholder for digits

words_processed = 0             # number of inputs words processed



### CLASSES ###

class RuleGen():
    '''
    generates rules based on wordlist
    optionally generate hashcat rules and/or displays report
    '''

    def __init__(self, in_list=[], cap=False, custom_digits=False):

        self.cap            = cap
        self.custom_digits  = custom_digits

        self.rules          = {}
        self.num_rules      = 0     # total not including duplicates
        self.total          = 0     # total including duplicates
        self.sorted_rules   = []

        for word in Grouper(in_list).parse():
            self.add(word)


    def report(self, display_limit=25):

        self.sort()

        display_count = 0
        display_len = 0
        for rule in self.sorted_rules[:display_limit]:
            display_count += rule[1]
            display_len += 1

        try:
            percent_displayed = (display_count / self.total) * 100
        except:
            assert False, 'No rules to display.'

        report = []

        title_str = '\n\nTop {:,} Rules out of {:,} ({:.1f}% coverage)'.format(display_len, self.num_rules, percent_displayed)
        report.append(title_str)
        report.append('='*len(title_str))

        for rule in self.sorted_rules[:display_len]:
            rule_bytes, rule_count = rule

            if self.custom_digits:
                rule_bytes = rule_bytes.replace(bytes(digit_delim), b'[digit]')

            rule_coverage = (rule_count / self.total) * 100
                
            report.append('{:>15,} ({:.1f}%):    {:<30}'.format(rule_count, rule_coverage, rule_bytes.replace(string_delim, b'[string]').decode()))

        return '\n'.join(report) + '\n'



    def dump(self, word_list, digit_list=[], d_key=lambda x: x, display_count=False):
        '''
        given wordlist, applies rules to each word and dumps to STDOUT
        '''

        stderr.write('\n')

        self.sort()

        _c = 0
        for word in word_list:

            c = 0
            for rule in self.sorted_rules:
                if display_count and _c % 1000 == 0:
                    stderr.write('\r[+] {:,} words written'.format(_c))

                rule = rule[0]

                try:
                    out_word = rule.replace(string_delim, word)
                    if self.custom_digits and digit_delim in out_word:
                        for digit in digit_list:
                            print( out_word.replace(digit_delim, d_key(digit)).decode() )
                            _c += 1
                    else:
                        print( out_word.decode() )
                        _c += 1

                    c += 1

                except UnicodeDecodeError:
                    continue

        if display_count:
            stderr.write('\r[+] {:,} words written\n'.format(_c))



    def write_rules(self, filename):
        '''
        writes hashcat rules
        '''

        self.sort()

        with open(filename, 'w') as f:

            c = 0

            for rule in self.sorted_rules:

                if string_delim in rule[0]:
                    if self.custom_digits and digit_delim in rule[0]:
                        for digit in self.custom_digits:
                            self._write_rule(rule[0].replace(digit_delim, digit), f)
                    else:
                        self._write_rule(rule[0], f)

                c += 1


    def add(self, groups):
        '''
        takes & parses already-split word
        '''

        num_groups = len(groups)

        # "passthrough" rule
        if num_groups == 1:
            try:
                self.rules[string_delim] += 1
            except KeyError:
                self.rules[string_delim] = 1
                self.num_rules += 1
            self.total += 1

        # skip generating rules for overly complex words
        elif num_groups > 5:
            return

        else:

            for index in range(num_groups):
                chartype = groups[index][0]
                if chartype == 2 or chartype == 4:
                    continue

                p1 = groups[:index]
                p2 = groups[index+1:]

                prepend = b''.join(g[1] for g in p1)
                append = b''.join(g[1] for g in p2)
                
                digit = False
                if self.custom_digits:

                    for p in range(len(p1)):
                        if p1[p][0] == 2:
                            new_prepend = list(p1)
                            new_prepend[p] = (2, digit_delim)
                            new_prepend = b''.join(g[1] for g in new_prepend)
                            rule = new_prepend + string_delim + append
                            self._add_rule(rule)
                            digit = True

                    for a in range(len(p2)):
                        if p2[a][0] == 2:
                            new_append = list(p2)
                            new_append[a] = (2, digit_delim)
                            new_append = b''.join(g[1] for g in new_append)
                            rule = prepend + string_delim + new_append
                            self._add_rule(rule)
                            digit = True

                # skip creating a rule if digits are enabled and a rule was already created
                if not digit:
                    rule = prepend + string_delim + append
                    self._add_rule(rule)


    def _add_rule(self, r):

        rules = Mutator([r], cap=self.cap).gen()

        c = 0
        for rule in rules:
            '''
            if digit:
                n = len(self.custom_digits)
                self.num_rules += n
                try:
                    self.rules[rule] += n
                except KeyError:
                    self.rules[rule] = n
                self.total += n
                    
            else:
            '''
            
            try:
                self.rules[rule] += 1
            except KeyError:
                self.rules[rule] = 1
                self.num_rules += 1

            # count the original word twice
            if self.cap and c == 0:
                self.rules[rule] += 1
                self.total += 1

            self.total += 1
            c += 1


    def _write_rule(self, rule, file):
        '''
        writes a single rule to an open file handle
        '''

        hc_rule = []

        prepend,append = rule.split(string_delim)
        if not (prepend or append):
            return

        for c in prepend:
            hc_rule.append('^' + chr(c))
        for c in append:
            hc_rule.append('$' + chr(c))

        file.write(' '.join(hc_rule) + '\n')


    def sort(self):

        if not self.sorted_rules:
            while self.rules:
                self.sorted_rules.append(self.rules.popitem())
            self.sorted_rules.sort(key=lambda x: x[1], reverse=True)


    def trim(self, length=None):

        self.sort()
        self.sorted_rules = self.sorted_rules[:length]





class WordGen():

    def __init__(self, in_list=[], digits=False, cap=False, capswap=False):
        '''
        accepts iterable of words from which to generate list
        of individual strings and/or digits
        '''
        
        # dictionary to hold common string/digit occurences
        # 1 = strings
        # 2 = digits
        # string/digit instances are stored in dictionary in the format: {occurence:count, ... }
        self.lists = {
            # chartype  list
            1:  {},
            2:  {}
        }

        self.num_words = {
            1: 0,
            2: 0
        }

        self.totals = {
            1: 0,
            2: 0
        }

        self.chartypes = {
            1: 'strings',
            2: 'digits'
        }

        self.in_list        = in_list
        self.digits         = digits
        self.sorted_words   = {1: [], 2: []}

        self.cap            = cap
        self.capswap        = capswap

        for word in Grouper(in_list).parse():
            self.add(word)


    def report(self, display_limit=25):
        '''
        returns (but does not print) report
        '''

        report = []

        self.sort()

        for chartype in self.chartypes:

            if not self.sorted_words[chartype]:
                continue

            display_count = 0
            display_len = 0
            for word in self.sorted_words[chartype][:display_limit]:
                display_count += word[1]
                display_len += 1

            try:
                percent_displayed = (display_count / self.totals[chartype]) * 100
            except:
                report.append('\nNo {} to display.\n'.format(self.chartypes[chartype]))

            title_str = '\n\nTop {:,} {} out of {:,} ({:.1f}% coverage)'.format(display_len, self.chartypes[chartype].capitalize(), self.num_words[chartype], percent_displayed)
            report.append(title_str)
            report.append('='*len(title_str))

            for word in self.sorted_words[chartype][:display_len]:
                string, count = word

                occurance = (count / self.totals[chartype]) * 100
                    
                report.append('{:>15,} ({:.1f}%):    {:<30}'.format(count, occurance, string.decode()))


        return '\n'.join(report) + '\n'


    def write(self, filename, digits=False):

        self.sort()

        filenames = {}
        
        for chartype in self.sorted_words:
            if (chartype == 2 and not digits): continue
            list_filename = str(filename) + '_' + self.chartypes[chartype]
            filenames[chartype] = list_filename
            with open(list_filename, 'wb') as f:
                for word in self.sorted_words[chartype]:
                    f.write(word[0] + b'\n')

        return filenames


    def add(self, grouped):

        for group in grouped:
            chartype, chunk = group

            if chartype == 4 or (chartype == 2 and not self.digits):
                continue

            chunks = [chunk]
            if chartype == 1:
                if self.capswap:
                    chunks = [chunk.lower()]
                elif self.cap:
                    chunks = [s for s in Mutator([chunk], cap=True).gen()]

            c = True
            for s in chunks:
                try:
                    self.lists[chartype][s] += 1
                except KeyError:
                    self.lists[chartype][s] = 1
                    self.num_words[chartype] += 1
                self.totals[chartype] += 1

                if chartype == 1 and c is True and self.cap:
                    self.lists[chartype][s] += 1
                    self.totals[chartype] += 1
                    c = False


    def sort(self):

        for chartype in self.sorted_words:

            if not self.sorted_words[chartype]:
                while self.lists[chartype]:
                    self.sorted_words[chartype].append(self.lists[chartype].popitem())
                self.sorted_words[chartype].sort(key=lambda x: x[1], reverse=True)



    def trim(self, lengths={1: None, 2: None}):

        self.sort()

        for chartype in lengths:
            self.sorted_words[chartype] = self.sorted_words[chartype][:lengths[chartype]]




class Mutator():

    def __init__(self, in_list, perm=0, leet=False, cap=False, capswap=False, key=lambda x: x):

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

        # max = maximum mutations per word
        # cur = used for carrying over unused mutations into next iteration
        self.max_leet       = max_leet
        self.max_cap        = max_cap
        self.cur_leet       = 0
        self.cur_cap        = 0

        self.perm_depth     = perm
        self.do_leet        = leet
        self.do_capswap     = capswap
        self.do_cap         = cap or capswap

        self.key            = key

        # calculate multiplier
        # num_mutations = (1 if cap else 0) + (1 if leet else 0)
        # self.multiplier = min(1, multiplier ** (1 / min(1, num_mutations)))


    def gen(self):
        '''
        generator function
        runs mangling functions on wordlist
        yields each mutated word
        '''

        for word in self.cap(self.leet(self.perm(self.in_list))):
            yield word


    def perm(self, in_list, repeat=True):
        '''
        permutates words from iterable
        takes:      iterable containing words
        yields:     word permutations ('pass', 'word' --> 'password', 'wordpass', etc.)
        '''

        if self.perm_depth > 1:

            words = [ self.key(w) for w in in_list ]
            
            for d in range(1, self.perm_depth+1):
                if repeat:
                    for p in itertools.product(words, repeat=d):
                        yield b''.join(p)

                else:
                    for p in itertools.permutations(words, d):
                        yield b''.join(p)
        else:
            for word in in_list:
                yield self.key(word)


    def cap(self, in_list):

        for word in in_list:

            yield word

            if self.do_cap:

                self.cur_cap += self.max_cap

                for r in self._cap(word):
                    self.cur_cap -= 1
                    yield r
                    if self.cur_cap <= 0:
                        break


    def leet(self, in_list):

        for word in in_list:

            yield word

            if self.do_leet:

                self.cur_leet += self.max_leet

                results = [] # list is almost 4 times faster than set
                num_results = 0

                gen_common = self._leet(word, swap_values=self.leet_common)
                for r in gen_common:
                    if r != word and not r in results:
                        if self.cur_leet <= 0:
                            break
                        results.append(r)
                        self.cur_leet -= 1
                        yield r

                gen_sparse = self._leet(word, swap_values=self.leet_all)
                for r in gen_sparse:
                    if r != word and not r in results:
                        if self.cur_leet <= 0:
                            break
                        results.append(r)
                        self.cur_leet -= 1
                        yield r


                self.cur_leet += (self.max_leet - len(results))

                results = []



    def _cap(self, word, swap=True):
        '''
        takes:      iterable containing words
        yields:     case variations (common only, unless 'all' is specified)
        '''

        # set type used to prevent duplicates
        results = []
        for r in [word.lower(), word.upper(), word.swapcase(), word.capitalize(), word.title()]:
            if r != word and r not in results:
                results.append(r)
                yield r

        if self.do_capswap:

            # oneliner which basically does it all
            for r in map(bytes, itertools.product(*zip(word.lower(), word.upper()))):
                if r != word and not r in results:
                    results.append(r)
                    yield r



    def _dict_str_to_bytes(self, d):

        new_dict = {}
        for key in d:
            new_dict[ord(key)] = [ord(v) for v in d[key]]
        return new_dict



    def _leet(self, word, swap_values=None):
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



class Grouper():
    '''
    Takes words as iterable of 'bytes' objects
    Yields each word, split by character type
    Format is ( (chartype, "chunk"), ... )
    '''

    def __init__(self, in_list, leet=True, progress=True):

        self.in_list    = in_list
        self.leet       = leet
        self.progress   = progress


    def parse(self):
        '''
        generator function
        parses list and yields each word, split into chunks based on chartype
        '''

        global words_processed

        for word in self.in_list:
            if self.progress == True and words_processed % 100 == 0:
                stderr.write('\r[+] {:,} words processed  '.format(words_processed))
            yield self.group_word(word)
            words_processed += 1

        stderr.write('\r[+] {:,} words processed  '.format(words_processed))


    def group_word(self, word):

        group_map = self.group_chartypes(word)
        groups = []

        for chunk in group_map:
            groups.append( ( chunk[0], word[ chunk[1][0]:chunk[1][1] ] ) )

        if self.leet:
            return self.group_l33t(groups)
        else:
            return groups


    def group_chartypes(self, b):

        group_map       = []
        # [ ( chartype, (start,end) ), ... ]

        start           = 0
        end             = 0
        group           = bytes()
        prev_chartype   = 0
        group_index     = 0

        for index in range(len(b)):
            chartype = self.get_chartype(b[index:index+1])

            if not chartype & prev_chartype:
                if start-end:
                    group_map.append( (prev_chartype, (start,end)) )
                    group_index += 1
                start = index

            end = index + 1
            prev_chartype = int(chartype)

        if start-end:
            group_map.append( (prev_chartype, (start,end)) )
            group_index += 1

        return group_map


    def get_chartype(self, char):

        if char.isalpha():
            return 1
        elif char.isdigit():
            return 2
        else:
            return 4


    def group_l33t(self, groups):

        try:
            assert len(groups) > 2
            # word must have at least two chartypes
            assert reduce( (lambda x,y: x|y), [v[0] for v in groups] ) not in (1,2,4)

            l33t_groups = []
            group_index = 0

            while 1:
                try:
                    if groups[group_index][0] & 1 > 0 and groups[group_index+1][0] & 6 > 0 and groups[group_index+2][0] & 1 > 0:

                        if all(c in leet_chars for c in groups[group_index+1][1]):
                            l33t_groups.append(self._combine_groups(groups[group_index:group_index+3]))
                            group_index += 3
                        else:
                            l33t_groups += groups[group_index:group_index+2]
                            group_index += 2

                    else:
                        l33t_groups.append(groups[group_index])
                        group_index += 1

                except IndexError:
                    l33t_groups += groups[group_index:]
                    break

            assert groups != l33t_groups
            return self.group_l33t(l33t_groups)

        except AssertionError:
            return groups


    def _combine_groups(self, groups):

        chartype    = groups[0][0] # just take chartype of first group
        string      = b''

        for group in groups:
            #chartype = chartype | group[0]
            string += group[1]

        return (chartype, string)



class ReadFile():

    def __init__(self, filename):

        self.filename = str(filename)
        assert(Path(self.filename).is_file()), 'Cannot find the file {}'.format(self.filename)


    def read(self):

        with open(self.filename, 'rb') as f:
            for line in f:
                try:
                    assert not string_delim in line
                    yield line.strip(b'\r\n')
                except AssertionError:
                    continue



class ReadSTDIN():

    def read(self):

        while 1:
            line = stdin.buffer.readline()
            if line:
                try:
                    assert not string_delim in line
                    yield line.strip(b'\r\n')
                except AssertionError:
                    continue
            else:
                break



class StretchStat():

    def __init__(self, rules=([], 0, 1), words=([], 0, 1), digits=([], 0, 1)):
        '''
        each arg is a tuple in the format:
        (counts, total, multiplier)
        '''
        self.rules  = ListStat(rules[0], rules[1], multiplier=rules[2], friendly='rules')
        self.words  = ListStat(words[0], words[1], multiplier=words[2], friendly='words')
        self.digits = ListStat(digits[0], digits[1], multiplier=digits[2], friendly='digits')


    def avg_percents(self):

        to_average = []

        for l in self:
            if l.percent:
                to_average.append(l.percent)

        return mean(to_average)


    def __iter__(self):

        yield self.words
        yield self.rules
        yield self.digits





class ListStat():
    '''
    Class for keeping track of each input list
    (words, digits, and rules) while truncating
    them to match desired crack time.
    '''

    def __init__(self, counts, total, multiplier=1, friendly=''):

        self.counts     = counts
        self.total      = total * multiplier    # total including duplicates (before trimming)
        self.current    = 0                     # current total including duplicates and mutations
                                                # used for calculating percent only
        self.multiplier = multiplier
        self.number     = 0                     # number - current total including mutations but not duplicates
        self.percent    = 0.0
        self.index      = 0                     # index - used for keeping track of place

        self.finished   = False

        self.friendly   = friendly


    def add_next(self):

        #count = counts[c][0][list_stats[c].index][1]
        count = self.counts[self.index]
        
        if type(count) == bytes:
            count = 1
        else:
            count = count[1]

        self.current += count * self.multiplier
        self.percent = (self.current / self.total) * 100
        self.index += 1
        self.number += self.multiplier


    def __str__(self):

        _str = ''
        _str += '{}:\n======================\n'.format(self.friendly.capitalize())
        _str += 'total:      {:,}\n'.format(self.total)
        _str += 'current:    {:,}\n'.format(self.current)
        _str += 'percent:    {:.2f}%\n'.format(self.percent)
        _str += 'number:     {:,}\n'.format(self.number)
        _str += 'index:      {:,}\n'.format(self.index)
        _str += 'multiplier: {:.3f}\n'.format(self.multiplier)
        _str += 'finished:   {}\n'.format(str(self.finished))

        return _str



### FUNCTIONS ###


def is_smaller(p, stretchers):

    percents = [l.percent for l in stretchers]

    if percents.count(p) > 1:
        return True

    return p != max(percents)



def calc_current_total(stretchers):
    '''
    calculates the total combined output of all lists currently
    in other words, num_words * num_digits * num_rules
    '''

    t = 1

    for l in stretchers:
        t *= max(1,l.number)

    return t

    #return reduce(lambda x,y:max(1,x)*max(1,y), [_.number for _ in stretchers])



def calc_max_inputs(stretchers, total_desired):
    '''
    calculates the maximum length of each input list (words, rules, digits) to meet the target time requirement

    note: the reason it's so complex is because it's taking *occurrence* into consideration
    this means that if the word 'password' occurs 50 times, every occurrence counts towards the percentage.
    '''

    left = 3

    while left > 0:
        for l in stretchers:

            current_total = calc_current_total(stretchers)
            if current_total < total_desired:

                if not l.finished:

                    try:
                        #count = l.counts[l.index][1]

                        if left == 1 or is_smaller(l.percent, stretchers):
                            l.add_next()

                    except IndexError:
                        l.finished = True
                        left -= 1

            else:
                left = 0
                break


    '''
    # fill up the empty space if we have any leftover room
    if current_total < total_desired:
        # count the number of 
        current_totals = []
        for l in stretchers:
            if l.current:
                current_totals.append(l.current)

        if len(current_totals) > 0:
            multiplier = total_desired / reduce(lambda x,y: x*y, current_totals)

        for l in stretchers:
            if l.current:
                l.current = int(l.current * multiplier)
    '''



def stretcher(options):

    global max_leet, max_cap

    # create words / rules objects
    words = WordGen(digits=options.common_digits, cap=options.cap, capswap=options.capswap)
    #words = WordGen(cap=options.cap, capswap=options.capswap)
    rules = RuleGen(cap=(options.cap or options.capswap), custom_digits=(options.common_digits or (True if options.digits else False)))


    try:
        # parse input
        for word in Grouper(options.wordlist.read()).parse():
            words.add(word)
            if not options.no_pend:
                rules.add(word)
    except KeyboardInterrupt:
        pass


    words.sort()
    rules.sort()


    d_key = lambda x: x
    if options.digits:
        d = options.digits
        d_total = len(options.digits)
    elif options.common_digits:
        d = words.sorted_words[2]
        d_total = words.totals[2]
        d_key = lambda x: x[0]
    else:
        d = []
        d_total = 0


    # account for cap / leet mutations by creating multipliers
    leet_size = (max_leet if options.leet else 1)
    if options.capswap:
        cap_size   = max_cap
    else:
        cap_size   = 1


    stretchers = StretchStat(rules=(rules.sorted_rules, rules.total, 1),\
                            words=(words.sorted_words[1], words.totals[1], (cap_size * leet_size)),\
                            digits=(d, d_total, 1))


    # total possible output before trimming takes place
    total_possible = max(1, len(words.sorted_words[1])) * max(1, len(d)) * max(1, len(rules.sorted_rules)) * stretchers.words.multiplier


    if options.target_time:

        total_desired = options.pps * int(options.target_time * 3600)

        calc_max_inputs(stretchers, total_desired)

        avg_percent_per_list = stretchers.avg_percents()

        # trim lists to newly calculated max lengths
        words.trim({1: stretchers.words.index, 2: stretchers.digits.index})
        d = d[:stretchers.digits.index]
        rules.trim(stretchers.rules.index)

    else:
        stretchers.rules.index = None
        stretchers.words.index = None
        stretchers.digits.index = None


    # total output after (optional) trimming
    total_actual = max(1, len(words.sorted_words[1])) * max(1, len(d)) * max(1, len(rules.sorted_rules)) * stretchers.words.multiplier


    # if there's still room to grow,
    # increase leet / cap output limits
    if options.target_time and (total_actual < total_desired) and (options.capswap or options.leet):
        num_mutations = min(1, (1 if options.capswap else 0) + (1 if options.leet else 0))
        multiplier = pow( (total_desired / total_actual), (1 / num_mutations) )

        max_leet = int(max_leet * multiplier)
        max_cap = int(max_cap * multiplier)

        stderr.write('\n[+] mutation cap increased to match desired time (multiplier: {:.4f})\n\n'.format(multiplier))

        total_actual = int(total_actual * multiplier)



    if options.strings:
        w_key = lambda x: x
        s = Mutator(options.strings, cap=options.cap, capswap=options.capswap, leet=options.leet, maximum=stretchers.words.index).gen()
        # string key - since sorted words appear in format (string, count),
        # we must give the option to only select the string only

    else:
        words.sort()
        w_key = lambda x: x[0]
        s = Mutator(words.sorted_words[1], capswap=options.capswap, leet=options.leet, key=w_key).gen()


    # print reports
    if options.report or options.hashcat:
        print(words.report(display_limit=options.report_size))
        print(rules.report(display_limit=options.report_size))
        print('\nWords processed:       {:>47,}'.format(words_processed))
        print('Possible combinations: {:>47,}'.format(total_possible))
        if options.target_time:
            print('Timeframe target:      {:>47,}'.format(total_desired))
        print('Actual combinations:   {:>47,}'.format(total_actual))
        print('=' * 70)
        print('Overall coverage:    {:>48.2f}%'.format(total_actual / total_possible * 100))

        if options.target_time:
            print('\nCoverage by type:')
            for l in stretchers:
                if l.current:
                    friendly = l.friendly + ':' + (' ' * (10 - len(l.friendly)))
                    print('    {}     {:.1f}% ({:,})'.format(friendly, l.percent, l.index))

        print('\nWordlist size:         {:>47}'.format(estimate_list_size(total_actual)))
        pps = 'Hours at {:,} pps:'.format(options.pps)
        hours = '{:.2f}'.format((total_actual / options.pps) / 3600)
        print(pps + ' '*(66-len(pps)+1-len(hours)) + hours + ' hrs')

    # if we're using hashcat
    if options.hashcat:

        # hashcat settings
        if 'ix' in os_type:
            posix       = True
            hc_binary   = 'hashcat'
        else:
            posix       = False
            hc_binary   = 'hashcat64.exe'

        options.hashcat.mkdir(parents=True, exist_ok=True)

        # filenames
        listname = str(options.hashcat / 'wordlist')
        rulename = str(options.hashcat / 'rules')
        scriptname = str(options.hashcat / 'hashcat.py')

        # write hashcat wordlist
        with open(listname, 'w') as f:

            for word in s:
                try:
                    f.write(word.decode() + '\n')
                except UnicodeDecodeError:
                    continue

        # write hashcat rules
        if not options.no_pend:
            rules.write_rules(rulename)
            rulestr = ['-r', rulename]
        else:
            rulestr = []

        # write hashcat script
        with open(scriptname, 'w') as f:

            def_opts = [ '"{}"'.format(o) for o in (['-w', '1', '-a', '0'] + rulestr) ]

            _help = ' Usage: {} [hashcat_opts] -m <hashtype> <hashfile>'.format(scriptname)

            lines = [
                '#!/usr/bin/env python3',
                'try:',
                '    from sys import argv',
                '    from subprocess import run',
                '    if len(argv) < 2 or any(a.startswith("-h") for a in argv) or any(a.startswith("--help") for a in argv):',
                '        print(" Usage: {} [hashcat_opts] -m <hashtype> <hashfile>".format(argv[0]))',
                '        exit(2)',
                '    hc_opts = argv[1:-1]',
                '    hashfile = argv[-1]',
                '    cmd = ["{}"] + hc_opts + [{}] + [hashfile] + ["{}"]'.format(hc_binary, ','.join(def_opts), listname),
                '    print("[+] " + " ".join(cmd) )',
                '    run(cmd)',
                'except KeyboardInterrupt:',
                '    print("\\n\\n[+] Program interrupted. ")'
            ]

            f.write('\n'.join(lines))

        stderr.write('\n[+] Hashcat resources written to {}\n'.format(str(options.hashcat)))
        stderr.write('[+] Please run: {} -h\n'.format(scriptname))


        if posix:
            Path(scriptname).chmod(0o755)


    # otherwise just dump passwords to stdout
    elif not options.report:
        display_count = not stdout.isatty()
        if options.no_pend:
            c = 0
            for _ in s:
                if display_count and c % 1000 == 0:
                    stderr.write('\r[+] {:,} words written'.format(c))
                print(_.decode())

            if display_count:
                stderr.write('\r[+] {:,} words written\n'.format(c))

        else:
            rules.dump(s, digit_list=d, d_key=d_key, display_count=display_count)



def read_file_or_str(s):

    try:
        entries = list(ReadFile(s).read())
    except AssertionError:
        entries = [e.encode() for e in s.split(',')]

    #for e in entries:
    #    yield e

    return entries



def estimate_list_size(n):

    # 9.75 = average bytes per line (including newlines) in rockyou
    # 1.4  = size adjustment for mangling
    return bytes_to_human(int(n * 9.75 * 1.4))



def bytes_to_human(_bytes):

    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
    units = {}
    count = 0
    for size in sizes:
        units[size] = pow(1024, count)
        count +=1

    for size in sizes:
        if abs(_bytes) < 1024.0:
            if size == sizes[0]:
                _bytes = str(int(_bytes))
            else:
                _bytes = '{:.2f}'.format(_bytes)
            return '{}{}'.format(_bytes, size)
        _bytes /= 1024

    raise ValueError




if __name__ == '__main__':

    ### ARGUMENTS ###

    parser = ArgumentParser(description="FETCH THE PASSWORD STRETCHER")

    parser.add_argument('-w', '--wordlist',         type=ReadFile,    default=ReadSTDIN(),      help="wordlist to analyze / stretch (default: STDIN)", metavar='')
    parser.add_argument('-r', '--report',           action='store_true',                        help="print report")
    parser.add_argument('--report-size',            type=int,         default=25,               help="maximum number of results in report", metavar='')

    parser.add_argument('-n', '--no-pend',          action='store_true',                        help="cap/leet mangling only - no appending/prepending")
    parser.add_argument('-hc', '--hashcat',         type=Path,                                  help="create hashcat resources in this folder", metavar='DIR')

    parser.add_argument('-t', '--target-time',      type=float,                                 help="desired maximum crack time in hours", metavar='')
    parser.add_argument('-p', '--pps',              type=int,         default=1000000,          help="expected hashrate (passwords per second)", metavar='')

    parser.add_argument('-s', '--strings',          type=read_file_or_str, default=[],          help="use these strings instead of those in the wordlist", metavar='')
    parser.add_argument('-d', '--digits',           type=read_file_or_str, default=[],          help="during rule generation, replace digits with these", metavar='')
    parser.add_argument('-g', '--common-digits',    action='store_true',                        help="during rule generation, replace digits with common occurrences")

    parser.add_argument('-L',   '--leet',           action='store_true',                        help="\"leetspeak\" mutations")
    parser.add_argument('-c',   '--cap',            action='store_true',                        help="common upper/lowercase variations")
    parser.add_argument('-C',   '--capswap',        action='store_true',                        help="all possible case combinations")
    #parser.add_argument('-P',   '--permutations',   type=int,           default=1,              help="Max times to combine words (careful! exponential)", metavar='INT')


    try:

        options = parser.parse_args()

        # print help if there's no arguments and no pipe to STDIN
        if not options.strings and type(options.wordlist) == ReadSTDIN and stdin.isatty():
            parser.print_help()
            stderr.write('\n [!] Please specify wordlist or pipe to STDIN\n')
            exit(2)

        if options.report_size != parser.get_default('report_size'):
            options.report = True

        stretcher(options)


    except ArgumentError:
        stderr.write("\n[!] Check your syntax. Use -h for help.\n")
        exit(2)
    except AssertionError as e:
        stderr.write("\n[!] {}\n".format(str(e)))
        exit(1)
    except KeyboardInterrupt:
        stderr.write("\n[!] Program interrupted.\n")
        exit(2)
