#!/usr/bin/env python3

'''

stretcher.py

by TheTechromancer

TODO:
    if total_actual < total_desired:
        apply multiplier to max_cap, max_leet


    change Mutator.cap() to output original word first
    change RuleGen & WordGen to count original twice

'''


import itertools
from time import sleep
from pathlib import Path
from statistics import mean
from functools import reduce
from os import name as os_type
from sys import argv, exit, stdin, stderr
from argparse import ArgumentParser, FileType, ArgumentError

### DEFAULTS ###

leet_chars      = (b'013578@$') # characters to consider "leet"

max_leet        = 64            # max number of leet mutations per word
max_cap         = 128           # max number of capitalization mutations per word

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

    def __init__(self, in_list=[], cap=False, custom_digits=[]):

        self.cap            = cap
        self.custom_digits  = list(custom_digits)

        self.rules          = {}
        self.num_rules      = 0     # total 
        self.total          = 0     # total including duplicates
        self.sorted_rules   = []
        #self.trimmed_rules  = []

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

            #b = '  {}:  "{}"'.format(str(rule_count), rule[0].replace(string_delim, b'__').decode())
            if self.custom_digits:
                rule_bytes = rule_bytes.replace(bytes(digit_delim), b'[digit]')

            rule_coverage = (rule_count / self.num_rules) * 100
                
            report.append('{:>15,} ({:.1f}%):    {:<30}'.format(rule_count, rule_coverage, rule_bytes.replace(string_delim, b'[string]').decode()))

        return '\n'.join(report) + '\n'



    def dump(self, word_list, key=lambda x: x):

        stderr.write('\n')

        self.sort()

        for word in word_list:


            c = 0
            for rule in self.sorted_rules:
                rule = rule[0]

                try:
                    out_word = rule.replace(string_delim, word)
                    if self.custom_digits and digit_delim in out_word:
                        for digit in self.custom_digits:
                            print( out_word.replace(digit_delim, digit).decode() )
                    else:
                        print( out_word.decode() )

                    c += 1

                except UnicodeDecodeError:
                    continue


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
        if not (num_groups > 1 and num_groups < 6):
            return

        for index in range(num_groups):
            chartype = groups[index][0]
            if chartype == 2 or chartype == 4:
                continue

            p1 = groups[:index]
            p2 = groups[index+1:]

            prepend = b''.join(g[1] for g in p1)
            append = b''.join(g[1] for g in p2)
            
            if self.custom_digits:

                for p in range(len(p1)):
                    if p1[p][0] == 2:
                        new_prepend = list(p1)
                        new_prepend[p] = (2, digit_delim)
                        new_prepend = b''.join(g[1] for g in new_prepend)
                        rule = new_prepend + string_delim + append
                        self._add_rule(rule, digit=True)

                for a in range(len(p2)):
                    if p2[a][0] == 2:
                        new_append = list(p2)
                        new_append[a] = (2, digit_delim)
                        new_append = b''.join(g[1] for g in new_append)
                        rule = prepend + string_delim + new_append
                        self._add_rule(rule, digit=True)

            else:

                rule = prepend + string_delim + append
                self._add_rule(rule)


    def _add_rule(self, r, digit=False):

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
            self.num_rules += 1
            try:
                self.rules[rule] += 1
            except KeyError:
                self.rules[rule] = 1

            # Add a mutated rule, but don't increment its counter
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
        '''
        if not self.trimmed_rules:
            c = 0
            while self.sorted_rules:
                if length and c > length:
                    break
                self.trimmed_rules.append(self.sorted_rules.pop(0)[0])
                c += 0
        '''





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

        self.totals = {
            1: 0,
            2: 0
        }

        self.chartypes = {
            1: 'words',
            2: 'digits'
        }

        self.in_list        = in_list
        self.digits         = digits
        self.sorted_words   = {1: [], 2: []}
        #self.trimmed_words  = {1: [], 2: []}

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

            title_str = '\n\nTop {:,} {} out of {:,} ({:.1f}% coverage)'.format(display_len, self.chartypes[chartype].capitalize(), len(self.sorted_words[chartype]), percent_displayed)
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
            chartype, string = group

            if chartype == 4 or (chartype == 2 and not self.digits):
                continue

            if self.capswap:
                strings = [string.lower()]
            elif self.cap:
                strings = [s for s in Mutator([string], cap=True).gen()]
            else:
                strings = [string]

            #c = 0
            for s in strings:
                try:
                    self.lists[chartype][s] += 1
                except KeyError:
                    self.lists[chartype][s] = 1
                self.totals[chartype] += 1

                #if c == 0 and self.cap:
                #    self.lists[chartype][s] += 1
                #    self.totals[chartype] += 1


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

        '''
        for chartype in lengths:

            maximum = lengths[chartype]

            c = 0
            while self.sorted_words[chartype]:
                if maximum and c > maximum:
                    break
                self.trimmed_words[chartype].append(self.sorted_words[chartype].pop(0)[0])
                c += 1
        '''




class Mutator():

    def __init__(self, in_list, perm=0, leet=False, cap=False, capswap=False, maximum=None, key=lambda x: x):

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

        self.maximum        = maximum

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

        c = 0
        for word in self.cap(self.leet(self.perm(self.in_list))):
            if self.maximum and c > self.maximum:
                break
            yield word
            c += 1


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

            if self.do_leet:

                self.cur_leet += self.max_leet

                results = [] # list is almost 4 times faster than set
                num_results = 0

                gen_common = self._leet(word, swap_values=self.leet_common)
                for r in gen_common:
                    if not r in results:
                        if self.cur_leet <= 0:
                            break
                        results.append(r)
                        self.cur_leet -= 1
                        yield r

                gen_sparse = self._leet(word, swap_values=self.leet_all, passthrough=False)
                for r in gen_sparse:
                    if not r in results:
                        if self.cur_leet <= 0:
                            break
                        results.append(r)
                        self.cur_leet -= 1
                        yield r


                self.cur_leet += (self.max_leet - len(results))

                results = []

            else:
                yield word


    def _cap(self, word, swap=True):
        '''
        takes:      iterable containing words
                    passthrough: whether or not to yield unmodified word
        yields:     case variations (common only, unless 'all' is specified)
        '''

        # set type used to prevent duplicates
        results = []
        self._uniq_add(results, word)
        self._uniq_add(results, word.lower())
        self._uniq_add(results, word.upper())
        self._uniq_add(results, word.swapcase())
        self._uniq_add(results, word.capitalize())
        self._uniq_add(results, word.title())

        for r in results:
            yield r

        if self.do_capswap:

            # oneliner which basically does it all
            for r in map(bytes, itertools.product(*zip(word.lower(), word.upper()))):
                if not r in results:
                    results.append(r)
                    yield r


    def _uniq_add(self, l, e):

        if not e in l:
            l.append(e)


    def _dict_str_to_bytes(self, d):

        new_dict = {}
        for key in d:
            new_dict[ord(key)] = [ord(v) for v in d[key]]
        return new_dict


    def _leet(self, word, swap_values=None, passthrough=True):
        '''
        takes:      iterable containing words
                    swap_values: dictionary containing leet swaps
                    passthrough: whether or not to yield unmodified word
        yields:     leet mutations, not exceeding max_results per word
        '''

        if not swap_values:
            swap_values = self.leet_all

        if passthrough:
            yield word

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
        self.processed  = 0


    def parse(self):
        '''
        generator function
        parses list and yields each word, split into chunks based on chartype
        '''

        for word in self.in_list:
            if self.progress == True and self.processed % 100 == 0:
                stderr.write('[+] {:,} words processed  \r'.format(self.processed))
            yield self.group_word(word)
            self.processed += 1

        stderr.write('[+] {:,} words processed  \r'.format(self.processed))

        global words_processed
        words_processed = self.processed


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




class ListStat():
    '''
    Class for keeping track of each input list
    (words, digits, and rules) while truncating
    them to match desired crack time.
    '''

    def __init__(self, total):

        self.total      = total     # total including duplicates (before trimming)
        self.current    = 0         # current total including duplicates and mutations
                                    # used for calculating percent only
        self.number     = 0         # current total including mutations but not duplicates
        self.percent    = 0.0

        self.index      = 0         # used for keeping track of place
        self.finished   = False


    def add(self, count, multiplier=1):

        self.current += count * multiplier
        self.percent = (self.current / self.total) * 100
        self.index += 1
        self.number += multiplier


    def __str__(self):

        _str = ''
        _str += 'ListStat:\n=========================\n'
        _str += 'total:   {:,}\n'.format(self.total)
        _str += 'current: {:,}\n'.format(self.current)
        _str += 'percent: {}\n'.format(self.percent)
        _str += 'number:  {:,}\n'.format(self.number)
        _str += 'index:   {:,}\n'.format(self.index)
        

        return _str



### FUNCTIONS ###


def calc_multiplier(lengths, pps, target_time, strings=False, digits=False, rules=True):
    '''
    TODO - maybe pass in full dictionaries rather than lengths
    let it iterate through all items (lists) like this:
    1. max_per_item *= len(item) * multiplier
    2. for each item:
            total *= num_items
            if not item.percent > (all the others)
                if total > total_desired:
                    break
                item.allowed += 1
                item.percent += (item.total / item[current].count)

    this way, lists with broader curves get higher priority (e.g. more words, less rules)
    '''

    # make sure lengths are all integers
    assert all( [type(i) == int for i in lengths] )

    # multiply all lengths together
    total_possible = reduce(lambda x,y: x*y, lengths)

    return min(1, (total_desired / total_possible) ** (1 / num_mutations))
    

    if not self.target_time:
        return 1

    num_mutations = min(1, (0 if strings else 1) + (1 if digits else 0) + (1 if rules else 0))

    total_desired = pps * (target_time * 3600)



def is_smaller(p, list_stats):

    percents = [l.percent for l in list_stats.values()]

    if percents.count(p) > 1:
        return True

    m = max(percents)
    if p < m:
        return True

    return False



def calc_current_total(list_stats):
    '''
    calculates the total combined output of all lists currently
    in other words, num_words * num_digits * num_rules
    '''

    return reduce(lambda x,y:max(1,x)*max(1,y), [l.number for l in list_stats.values()])



def calc_max_inputs(counts, multipliers, total_desired):
    '''
    calculates the maximum length of each input list (words, rules, digits) to meet the target time requirement

    note: the reason it's so complex is because it's taking *occurrence* into consideration
    this means that if the word 'password' occurs 50 times, every occurrence counts towards the percentage.
    '''

    list_stats = dict()
    for c in counts:
        list_stats[c] = ListStat(counts[c][1])

    left = len(counts)

    while left:
        for c in counts:

            current_total = calc_current_total(list_stats)

            #print('current', current_total, 'desired', total_desired)

            if current_total < total_desired:
            
                if not list_stats[c].finished:

                    try:
                        count = counts[c][0][list_stats[c].index][1]

                        if left == 1 or is_smaller(list_stats[c].percent, list_stats):
                            list_stats[c].add(count, multipliers[c])

                            #current_total += (count * m)
                            

                    except IndexError:
                        list_stats[c].finished = True
                        left -= 1

            else:
                left = 0
                break

            #else:
            #    print('\n\nCURRENT: {}\nDESIRED: {}\n\n'.format(current_total, total_desired))
            #    left = 0


    # fill up the empty space if we have any leftover room
    if current_total < total_desired:
        # count the number of 
        current_totals = []
        for c in list_stats:
            if list_stats[c].current:
                current_totals.append(list_stats[c].current)

        if len(current_totals) > 0:
            multiplier = total_desired / reduce(lambda x,y: x*y, current_totals)

        for c in list_stats:
            if list_stats[c].current:
                list_stats[c].current = int(list_stats[c].current * multiplier)


    '''
    current_total = calc_current_total(list_stats)
    if current_total < total_desired:
        # count the number of 
        current_totals = []
        for c in list_stats:
            if list_stats[c].current:
                current_totals.append(list_stats[c].current)

        if len(current_totals) > 0:
            leftover = int( (total_desired - current_total) ** (1 / num_lists) )

            for c in list_stats:
                if list_stats[c].current:
                    print('\n', c, list_stats[c].current, total_desired - current_total, leftover, '\n')
                    list_stats[c].current += leftover
    '''


    #final_counts = {}
    #for k in list_stats:
    #    final_counts[k] = list_stats[k].current

    return list_stats



def stretcher(options):

    # create words / rules objects
    words = WordGen(digits=(True if options.digits else False), cap=options.cap, capswap=options.capswap)
    words = WordGen(cap=options.cap, capswap=options.capswap)
    rules = RuleGen(cap=(options.cap or options.capswap), custom_digits=options.digits)


    '''
    if type(options.wordlist) == ReadSTDIN:
        multiplier = 1
    else:
        
        # l = [ (number of words) + (number of digits) + (number of rules) ]
        l = [ (len(options.strings) if options.strings else len(words.lists[1])), len(words.lists[2]), len(rules.rules) ]
        multiplier = calc_multiplier(l, pps, self.target_time, strings=options.strings, digits=options.digits, rules=options.rules)
    '''


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

    # account for cap / leet mutations by creating multipliers
    leet_size = (max_leet if options.leet else 1)
    if options.capswap:
        cap_size   = max_cap
    elif options.cap:
        cap_size   = 5
    else:
        cap_size   = 1

    multipliers = {
        'rules': 1,
        'words': cap_size * leet_size,
        'digits': 1
    }


    # total possible output before trimming takes place
    #print('\n')
    #print(', '.join([str(len(words.sorted_words[1])), str(len(rules.sorted_rules)), str(multipliers['words'])]))
    total_possible = len(words.sorted_words[1]) * len(rules.sorted_rules) * multipliers['words']


    if options.target_time:

        total_desired = options.pps * int(options.target_time * 3600)

        #print('\nTOTAL DESIRED: {:,}\n'.format(total_desired))

        list_stats = calc_max_inputs({
                    'words': (words.sorted_words[1], words.totals[1] * multipliers['words']),
                    'digits': (words.sorted_words[2], words.totals[2]),
                    'rules': (rules.sorted_rules, rules.total)},
                    multipliers, total_desired)
        
        #for k in list_stats:
        #    print(k)
        #    print(str(list_stats[k]))

        to_average = []
        for l in list_stats.values():
            if l.percent:
                to_average.append(l.percent)
        avg_percent_per_list = mean(to_average)

        max_inputs = {}
        for k in list_stats:
            #print(k, list_stats[k].total, list_stats[k].current)
            max_inputs[k] = list_stats[k].index

        rules.custom_digits = rules.custom_digits[:max_inputs['digits']]
        words.trim({1: max_inputs['words'], 2: max_inputs['digits']})
        rules.trim(max_inputs['rules'])

    else:
        max_inputs = {'rules': None, 'words': None, 'digits': None}


    # total output after (optional) trimming
    total_actual = len(words.sorted_words[1]) * len(rules.sorted_rules) * multipliers['words']


    if options.strings:
        s_key = lambda x: x
        s = Mutator(options.strings, cap=options.cap, capswap=options.capswap, leet=options.leet, maximum=max_inputs['words']).gen()
        # string key - since sorted words appear in format (string, count),
        # we must give the option to only select the string only

    else:
        words.sort()
        s_key = lambda x: x[0]
        s = Mutator(words.sorted_words[1], capswap=options.capswap, leet=options.leet, maximum=max_inputs['words'], key=s_key).gen()


    # print reports
    if options.report or options.hashcat:
        print(words.report())
        print(rules.report())
        print('\nWords processed:             {:,}'.format(words_processed))
        print('Possible combinations:       {:,}'.format(total_possible))
        if options.target_time:
            print('Timeframe target:            {:,}'.format(total_desired))
        print('Actual combinations:         {:,}'.format(total_actual))
        print('=============================================')
        print('Overall coverage:            {:.2f}%'.format(total_actual / total_possible * 100))

        if options.target_time:
            print('\nCoverage by type:')
            for k in list_stats:
                #print(str(list_stats[k]))
                if list_stats[k].current:
                    print('    {}:     {:.1f}%'.format(k, list_stats[k].percent))

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
                'from sys import argv',
                'from subprocess import run',
                'if len(argv) < 2 or any(a.startswith("-h") for a in argv) or any(a.startswith("--help") for a in argv):',
                '    print(" Usage: {} [hashcat_opts] -m <hashtype> <hashfile>".format(argv[0]))',
                '    exit(2)',
                'hc_opts = argv[1:-1]',
                'hashfile = argv[-1]',
                'cmd = ["{}"] + hc_opts + [{}] + [hashfile] + ["{}"]'.format(hc_binary, ','.join(def_opts), listname),
                'print("[+] " + " ".join(cmd) )',
                'run(cmd)'
            ]

            f.write('\n'.join(lines))

        stderr.write('\n[+] Hashcat resources written to {}\n'.format(str(options.hashcat)))
        stderr.write('[+] Please run: {} -h\n'.format(scriptname))


        if posix:
            Path(scriptname).chmod(0o755)


    # otherwise just dump passwords to stdout
    elif not options.report:
        if options.no_pend:
            for _ in s:
                print(_.decode())
        else:
            rules.dump(s, key=s_key)



def read_file_or_str(s):

    try:
        entries = ReadFile(s).read()
    except AssertionError:
        entries = [e.encode() for e in s.split(',')]

    for e in entries:
        yield e


def estimate_list_length(f):

    f = Path(f)
    size = f.stat().st_size
    # 9.75 = average bytes per line (including newlines) in rockyou
    return int(size / 9.75)



if __name__ == '__main__':

    ### ARGUMENTS ###

    parser = ArgumentParser(description="FETCH THE PASSWORD STRETCHER")

    parser.add_argument('-w', '--wordlist',         type=ReadFile,    default=ReadSTDIN(),      help="wordlist to analyze / stretch (default: STDIN)", metavar='')
    parser.add_argument('-r', '--report',           action='store_true',                        help="print report")

    parser.add_argument('-n', '--no-pend',          action='store_true',                        help="mangle only - no appending/prepending")
    parser.add_argument('-hc', '--hashcat',         type=Path,                                  help="create hashcat resources in this folder", metavar='DIR')

    parser.add_argument('-t', '--target-time',      type=float,                                 help="desired maximum crack time in hours", metavar='')
    parser.add_argument('-p', '--pps',              type=int,         default=1000000,          help="expected hashrate (packets per second)", metavar='')

    parser.add_argument('-s', '--strings',          type=read_file_or_str, default=[],          help="use these strings instead of those in the wordlist", metavar='')
    parser.add_argument('-d', '--digits',           type=read_file_or_str, default=[],          help="use these digits instead of those in the wordlist", metavar='')

    parser.add_argument('-L',   '--leet',           action='store_true',                        help="\"leetspeak\" mutations")
    parser.add_argument('-c',   '--cap',            action='store_true',                        help="common upper/lowercase variations")
    parser.add_argument('-C',   '--capswap',        action='store_true',                        help="all possible case combinations")
    #parser.add_argument('-P',   '--permutations',   type=int,           default=1,              help="Max times to combine words (careful! exponential)", metavar='INT')


    try:

        options = parser.parse_args()

        # print help if there's no arguments and no pipe to STDIN
        if not options.strings and type(options.wordlist) == ReadSTDIN and stdin.isatty():
            #if not options.strings:
            #if stdin.isatty():
            parser.print_help()
            stderr.write('\n [!] Please specify wordlist or pipe to STDIN\n')
            exit(2)

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
