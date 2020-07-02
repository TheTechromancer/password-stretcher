#!/usr/bin/env python3

'''

by TheTechromancer

'''

import os
import sys
from time import sleep
from lib.utils import *
from lib.errors import *
from lib.mangler import *
from lib.spider import Spider
from argparse import ArgumentParser, ArgumentError



def stretcher(options):

    if options.min_length is not None and options.max_length is not None:
        if options.min_length > options.max_length:
            print('U WOT M8')
            sys.exit()

    show_written_count = not sys.stdout.isatty()
    written_count = 0

    sys.stderr.write('[+] Reading input wordlist...')
    mangler = Mangler(
        _input=options.input,
        output_size=options.limit,
        double=options.double,
        perm=options.permutations,
        leet=options.leet,
        cap=options.cap,
        capswap=options.capswap,
        pend=options.pend,
    )
    sys.stderr.write(f' read {len(mangler.input):,} words {"(after basic cap mutations)" if (options.cap and not options.capswap) else ""}\n')
    if options.permutations > 1:
        sys.stderr.write(f'[*] Input wordlist after permutations: {len(mangler.mutators[0]):,}\n')
    else:
        sys.stderr.write(f'[*] Output capped at {mangler.output_size:,} words\n')
    if any([mangler.leet, mangler.cap, mangler.pend]):
        sys.stderr.write('[+] Mutations allowed per word:\n')
        for mutator in mangler.mutators[1:]:
            sys.stderr.write(f'       {str(mutator):<16}{mutator.limit:,}\n')
    if options.min_length is not None:
        sys.stderr.write(f'[+] Discarding words shorter than {options.min_length:,} characters, output size may be reduced\n')
    if options.max_length is not None:
        sys.stderr.write(f'[+] Discarding words longer than {options.max_length:,} characters, output size may be reduced\n')

    #sys.stderr.write(f'[+] Estimated output: {len(mangler):,} words\n')

    bytes_written = 0
    for mangled_word in mangler:

        if (options.min_length is None or len(mangled_word) >= options.min_length) and \
            (options.max_length is None or len(mangled_word) <= options.max_length):

            sys.stdout.buffer.write(mangled_word + b'\n')
            bytes_written += (len(mangled_word)+1)
            if show_written_count and written_count % 10000 == 0:
                sys.stderr.write(f'\r[+] {written_count:,} words written ({bytes_to_human(bytes_written)})    ')

            written_count += 1

        else:
            # if the word didn't meet length requirements, increase the limit by 1
            mangler.mutators[-1].cur_limit += 1

    if show_written_count:
        sys.stderr.write(f'\r[+] {written_count:,} words written ({bytes_to_human(bytes_written)})    \n')

    sys.stdout.buffer.flush()
    sys.stdout.close()



if __name__ == '__main__':

    ### ARGUMENTS ###

    parser = ArgumentParser(description='FETCH THE PASSWORD STRETCHER')

    parser.add_argument('-i',       '--input',          type=read_uri,    default=ReadSTDIN(),      help='input website or wordlist (default: STDIN)', metavar='')
    parser.add_argument('-L',       '--leet',           action='store_true',                        help='"leetspeak" mutations')
    parser.add_argument('-c',       '--cap',            action='store_true',                        help='common upper/lowercase variations')
    parser.add_argument('-C',       '--capswap',        action='store_true',                        help='all possible case combinations')
    parser.add_argument('-p',       '--pend',           action='store_true',                        help='append/prepend common digits & special characters')
    parser.add_argument('-dd',      '--double',         action='store_true',                        help='double each word (e.g. "Pass" --> "PassPass")')
    parser.add_argument('-P',       '--permutations',   type=int,               default=1,          help='max permutation depth (careful! massive output)', metavar='INT')
    parser.add_argument('-m',       '--min-length',     type=int,                                   help='minimum password length (for output)', metavar='INT')
    parser.add_argument('-M',       '--max-length',     type=int,                                   help='maximum password length (for output)', metavar='INT')
    parser.add_argument('--limit',                      type=human_to_int,                          help='limit length of output (default: max(100M, 1000x input))')
    parser.add_argument('--spider-depth',               type=int,               default=1,          help='maximum website spider depth (default: 1)')

    try:

        options = parser.parse_args()

        # print help if there's nothing to stretch
        if type(options.input) == ReadSTDIN and stdin.isatty():
            parser.print_help()
            sys.stderr.write('\n\n[!] Please specify wordlist or pipe to STDIN\n')
            exit(2)

        elif type(options.input) == Spider:
            options.input.depth = options.spider_depth
            options.input.start()

        stretcher(options)

    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
    except PasswordStretcherError as e:
        sys.stderr.write(f'\n[!] {e}\n')
        exit(1)
    except ArgumentError:
        sys.stderr.write('\n[!] Check your syntax. Use -h for help.\n')
        exit(2)
    except AssertionError as e:
        sys.stderr.write('\n[!] {}\n'.format(str(e)))
        exit(1)
    except KeyboardInterrupt:
        sys.stderr.write('\n[!] Interrupted.\n')
        exit(2)