#!/usr/bin/env python3

'''
TODO:

# hashcat rules
RuleGen.write(self, percent=90):

# output string list
class WordGen():

# overseer
class Overseer():
    1. generate lists (put in /tmp if not hashcat)
    2. generate rules (put in /tmp if not hashcat)
    3. if hashcat: generate scripts
    3. else: output to stdout


'''
import pickle
import itertools
from time import sleep
from pathlib import Path
from functools import reduce
from os import name as os_type
from sys import exit, stdin, stderr
from argparse import ArgumentParser, FileType, ArgumentError

### DEFAULTS ###

leet_chars      = (b'013578@$') # characters to consider "leet"

max_leet        = 64            # max number of leet mutations per word
max_cap         = 128           # max number of capitaliztion mutations per word

report_limit    = 50            # maximum lines for each individual report

string_delim    = b'\x00'       # unique unprintable placeholder for strings
digit_delim     = b'\x01'       # unique unprintable placeholder for digits



### CLASSES ###

class RuleGen():
    '''
    generates rules based on wordlist
    optionally generate hashcat rules and/or displays report
    '''

    def __init__(self, in_list=[], cap=False, custom_digits=[]):

        self.cap = cap
        self.custom_digits = list(custom_digits)

        self.rules = {}
        self.num_rules = 0
        self.sorted_rules = []

        for word in Grouper(in_list).parse():
            self.add(word)


    def report(self, display_limit=50):

        self._sort()

        display_count = 0
        display_len = 0
        for rule in self.sorted_rules[:display_limit]:
            display_count += rule[1]
            display_len += 1

        try:
            percent_displayed = (display_count / self.num_rules) * 100
        except:
            assert False, 'No rules to display.'

        report = []

        title_str = '\n\nTop {:,} Rules out of {:,} ({:.1f}% coverage)'.format(display_len, len(self.sorted_rules), percent_displayed)
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



    def dump(self, word_list):

        self._sort()

        print('')

        for word in word_list:
            for rule in self.sorted_rules:
                rule = rule[0]
                try:
                    out_word = rule.replace(string_delim, word)
                    if self.custom_digits and digit_delim in out_word:
                        for digit in self.custom_digits:
                            print( out_word.replace(digit_delim, digit).decode() )
                    else:
                        print( out_word.decode() )

                except UnicodeDecodeError:
                    continue


    def write_rules(self, filename):
        '''
        writes hashcat rules
        '''

        self._sort()

        with open(filename, 'w') as f:

            for rule in self.sorted_rules:

                if string_delim in rule[0]:
                    if self.custom_digits and digit_delim in rule[0]:
                        for digit in self.custom_digits:
                            self._write_rule(rule[0].replace(digit_delim, digit), f)
                    else:
                        self._write_rule(rule[0], f)


    def add(self, groups):
        '''
        takes & parses already-split word
        '''

        num_groups = len(groups)
        if not num_groups > 1 and num_groups < 6:
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


    def _add_rule(self, rule, digit=False):

        if self.cap:
            rules = Mutator([rule], cap=True).gen()
        else:
            rules = [rule]

        c = 0
        for rule in rules:
            if digit:
                n = len(self.custom_digits)
                self.num_rules += n
                try:
                    self.rules[rule] += n
                except KeyError:
                    self.rules[rule] = n
                    
            else:
                self.num_rules += 1
                try:
                    self.rules[rule] += 1
                except KeyError:
                    self.rules[rule] = 1

                # Add a mutated rule, but don't increment its counter
                if self.cap and c != 0:
                    self.rules[rule] -= 1

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


    def _sort(self):

        if not self.sorted_rules:
            self.sorted_rules = list(self.rules.items())
            self.sorted_rules.sort(key=lambda x: x[1], reverse=True)
            # clear dictionary to save memory
            self.rules = {}




class WordGen():

    def __init__(self, in_list=[], digits=False, cap=False, capswap=False, leet=False):
        '''
        accepts iterable of words from which to generate list
        of individual strings and/or digits
        '''

        self.cap        = cap
        self.capswap    = capswap
        self.leet       = leet
        self.mutate     = (cap or capswap or leet)
        
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

        for word in Grouper(in_list).parse():
            self.add(word)


    def report(self, display_limit=50):
        '''
        returns (but does not print) report
        '''

        report = []

        self._sort()

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

        self._sort()

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

            if self.mutate:
                words = Mutator([string], cap=self.cap, capswap=self.capswap, leet=self.leet).gen()
            else:
                words = [string]

            c = 0
            for word in words:
                try:
                    self.lists[chartype][word] += 1
                except KeyError:
                    self.lists[chartype][word] = 1
                self.totals[chartype] += 1

                # only count first (non-mutated) occurrence
                if self.mutate and c != 0:
                    self.lists[chartype][word] -= 1
                    self.totals[chartype] -= 1

                c += 1


    def _sort(self):

        for chartype in self.sorted_words:
            if not self.sorted_words[chartype]:
                self.sorted_words[chartype] = list(self.lists[chartype].items())
                self.sorted_words[chartype].sort(key=lambda x: x[1], reverse=True)

            # clear dictionary to save memory
            self.lists[chartype] = {}



class Mutator():

    def __init__(self, in_list, perm=0, leet=False, cap=False, capswap=False, grouped=False):

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

        # whether or not the words have been grouped
        self.grouped        = grouped


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

            if self.grouped:
                words = [ w[0] for w in in_list ]
            else:
                words = [w for w in in_list ]
            
            for d in range(1, self.perm_depth+1):
                if repeat:
                    for p in itertools.product(words, repeat=d):
                        yield b''.join(p)

                else:
                    for p in itertools.permutations(words, d):
                        yield b''.join(p)
        else:
            for word in in_list:
                if self.grouped:
                    yield word[0]
                else:
                    yield word


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
                stderr.write('  {:,} words processed  \r'.format(self.processed))
            yield self.group_word(word)
            self.processed += 1 


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
            assert reduce( (lambda x,y: x&y), [v[0] for v in groups] ) not in (1,2,4)

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



### FUNCTIONS ###


def stretcher(options):

    # hashcat settings
    if 'ix' in os_type:
        posix       = True
        hc_binary   = 'hashcat'
    else:
        posix       = False
        hc_binary   = 'hashcat64.exe'

    # create words / rules objects
    words = WordGen(digits=(True if options.digits else False), cap=options.cap, capswap=options.capswap, leet=options.leet)
    rules = RuleGen(cap=options.cap, custom_digits=options.digits)

    try:
        # parse input
        for word in Grouper(options.wordlist.read()).parse():
            words.add(word)
            if not options.no_rules:
                rules.add(word)
    except KeyboardInterrupt:
        pass

    # print reports
    if options.report:
        print(words.report())
        print(rules.report())
        total_possible = len(words.sorted_words[1]) * len(rules.sorted_rules)
        print('Total possible combinations: {:,}'.format(total_possible))

    # set up common strings with optional mutations
    # def __init__(self, in_list, perm=0, leet=True, cap=True, capswap=True):
    words._sort()
    s = words.sorted_words[1]
    #m = Mutator(words.sorted_words[1], perm=0, leet=options.leet, cap=options.cap, capswap=options.capswap, grouped=True).gen()

    if options.no_rules:
        for word in s:
            print(word[0].decode())

    # hashcat stuff
    elif options.hashcat:

        options.hashcat.mkdir(parents=True, exist_ok=True)

        # filenames
        listname = str(options.hashcat / 'wordlist')
        rulename = str(options.hashcat / 'rules')
        scriptname = str(options.hashcat / 'hashcat.py')

        # write hashcat wordlist
        with open(listname, 'w') as f:
            #for word in m:
            for word in s:
                try:
                    f.write(word[0].decode() + '\n')
                except UnicodeDecodeError:
                    continue

        # write hashcat rules
        rules.write_rules(rulename)

        # write hashcat script
        with open(scriptname, 'w') as f:

            def_opts = [ '"{}"'.format(o) for o in ['-w', '1', '-a', '0', '-r', rulename] ]

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


        if posix:
            Path(scriptname).chmod(0o755)

    # or just write to stdout
    elif not options.report:
        rules.dump(s)



def read_file_or_str(s):

    try:
        digits = ReadFile(s).read()
    except AssertionError:
        digits = [d.encode() for d in s.split(',')]

    for d in digits:
        yield d



if __name__ == '__main__':

    ### ARGUMENTS ###

    parser = ArgumentParser(description="FETCH THE PASSWORD STRETCHER")

    parser.add_argument('-w', '--wordlist',         type=ReadFile,    default=ReadSTDIN(),      help="wordlist to mangle (default: STDIN)", metavar='LIST')
    parser.add_argument('-s', '--save',             type=Path,                                  help="save individual strings/digits in this file", metavar='FILE')
    parser.add_argument('-r', '--report',           action='store_true',                        help="print report")

    parser.add_argument('-n', '--no-rules',         action='store_true',                        help="mangle only - no appending/prepending")

    parser.add_argument('-hc', '--hashcat',         type=Path,                                  help="create hashcat script in this folder", metavar='DIR')

    parser.add_argument('--strings',                type=read_file_or_str, default=[],          help="generate passwords using these strings instead")
    parser.add_argument('-d', '--digits',           type=read_file_or_str, default=[],          help="generate passwords using these digits instead")

    parser.add_argument('-L',   '--leet',           action='store_true',                        help="\"leetspeak\" mutations")
    parser.add_argument('-c',   '--cap',            action='store_true',                        help="common upper/lowercase variations")
    parser.add_argument('-C',   '--capswap',        action='store_true',                        help="all possible case combinations")
    #parser.add_argument('-P',   '--permutations',   type=int,           default=1,              help="Max times to combine words (careful! exponential)", metavar='INT')


    try:

        options = parser.parse_args()
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
