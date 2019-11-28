#!/usr/bin/env python3

'''

by TheTechromancer

'''

from time import sleep
from lib.utils import *
from lib.mangler import *
from sys import exit, stdin, stderr, stdout
from argparse import ArgumentParser, ArgumentError




def stretcher(options):

    show_written_count = not stdout.isatty()
    written_count = 0

    stderr.write('[+] Reading input wordlist...')
    mangler = Mangler(
        in_list=options.input,
        output_size=options.limit,
        double=options.double,
        perm=options.permutations,
        leet=options.leet,
        cap=options.cap,
        capswap=options.capswap,
    )
    stderr.write(f' read {len(mangler.in_list):,} words.\n')
    stderr.write(f'[*] Output capped at {mangler.output_size:,} words\n')
    if any([mangler.do_leet, mangler.do_cap]):
        stderr.write('[+] Mutations allowed per word:\n')
        if mangler.do_leet:
            stderr.write(f'     - leet:           {mangler.max_leet:,}\n')
        if mangler.do_capswap:
            stderr.write(f'     - capitalization: {mangler.max_cap:,}\n')
        elif mangler.do_cap:
            stderr.write(f'     - capitalization: 6\n')

    #stderr.write(f'[+] Estimated output: {len(mangler):,} words\n')

    bytes_written = 0
    for mangled_word in mangler:

        stdout.buffer.write(mangled_word + b'\n')
        bytes_written += (len(mangled_word)+1
            )
        if show_written_count and written_count % 10000 == 0:
            stderr.write(f'\r[+] {written_count:,} words written ({bytes_to_human(bytes_written)})    ')

        written_count += 1

    if show_written_count:
        stderr.write(f'\r[+] {written_count:,} words written ({bytes_to_human(bytes_written)})    \n')

    stdout.buffer.flush()
    stdout.close()



if __name__ == '__main__':

    ### ARGUMENTS ###

    parser = ArgumentParser(description="FETCH THE PASSWORD STRETCHER")

    parser.add_argument('-i',       '--input',          type=ReadFile,    default=ReadSTDIN(),      help="wordlist to stretch (default: STDIN)", metavar='')
    parser.add_argument('-L',       '--leet',           action='store_true',                        help="\"leetspeak\" mutations")
    parser.add_argument('-c',       '--cap',            action='store_true',                        help="common upper/lowercase variations")
    parser.add_argument('-C',       '--capswap',        action='store_true',                        help="all possible case combinations")
    parser.add_argument('-dd',      '--double',         action='store_true',                        help="double each word (e.g. \"Pass\" --> \"PassPass\")")
    parser.add_argument('-P',       '--permutations',   type=int,               default=1,          help="max permutation depth (careful! massive output)", metavar='INT')
    parser.add_argument('--limit',                      type=human_to_int,                          help="limit length of output (default: max(100M, 1000x input))")


    try:

        options = parser.parse_args()

        # print help if there's nothing to stretch
        if type(options.input) == ReadSTDIN and stdin.isatty():
            parser.print_help()
            stderr.write('\n\n[!] Please specify wordlist or pipe to STDIN\n')
            exit(2)

        stretcher(options)


    except ArgumentError:
        stderr.write("\n[!] Check your syntax. Use -h for help.\n")
        exit(2)
    except AssertionError as e:
        stderr.write("\n[!] {}\n".format(str(e)))
        exit(1)
    except KeyboardInterrupt:
        stderr.write("\n[!] Interrupted.\n")
        exit(2)