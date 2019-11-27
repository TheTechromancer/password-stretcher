#!/usr/bin/env python3

'''

by TheTechromancer

'''

from time import sleep
from lib.utils import *
from pathlib import Path
from lib.mangler import *
from statistics import mean
from functools import reduce
from os import name as os_type
from sys import argv, exit, stdin, stderr, stdout
from argparse import ArgumentParser, FileType, ArgumentError




def stretcher(options):

    show_written_count = not stdout.isatty()
    written_count = 0

    mangler = Mangler(
        in_list=options.wordlist,
        double=options.double,
        perm=options.permutations,
        leet=options.leet,
        cap=options.cap,
        capswap=options.capswap,
    )

    if options.target_size:
        stderr.write(f'[+] Requested output size: {bytes_to_human(options.target_size)} (approximately {int(options.target_size / (mangler.average_word_size)):,} words)\n')
        mangler.set_output_size(options.target_size)
        stderr.write(f'    - input size:            {len(mangler.in_list):,} words\n')
        stderr.write(f'    - average word length:   {mangler._average_word_size:.2f}\n')
        if mangler.perm_depth > 1:
            stderr.write(f'    - with permutations:     {mangler.average_word_size:.2f}\n')
        if mangler.do_leet:
            stderr.write(f'    - max_leet:              {mangler.max_leet:,}\n')
        if mangler.do_capswap:
            stderr.write(f'    - max_cap:               {mangler.max_cap:,}\n')

    stderr.write(f'[+] Estimated output: {len(mangler):,} words ({bytes_to_human(mangler.output_size)})\n')
    sleep(3)

    for mangled_word in mangler:

        stdout.buffer.write(mangled_word + b'\n')
        if show_written_count and written_count % 1000 == 0:
            stderr.write('\r[+] {:,} words written'.format(written_count))

        written_count += 1

    if show_written_count:
        stderr.write('\r[+] {:,} words written\n'.format(written_count))

    stdout.buffer.flush()
    stdout.close()



if __name__ == '__main__':

    ### ARGUMENTS ###

    parser = ArgumentParser(description="FETCH THE PASSWORD STRETCHER")

    parser.add_argument('-r',       '--wordlist',       type=ReadFile,    default=ReadSTDIN(),      help="wordlist to analyze / stretch (default: STDIN)", metavar='')
    parser.add_argument('-L',       '--leet',           action='store_true',                        help="\"leetspeak\" mutations")
    parser.add_argument('-c',       '--cap',            action='store_true',                        help="common upper/lowercase variations")
    parser.add_argument('-C',       '--capswap',        action='store_true',                        help="all possible case combinations")
    parser.add_argument('-dd',      '--double',         action='store_true',                        help="double each word (e.g. \"Pass\" --> \"PassPass\")")
    parser.add_argument('-P',       '--permutations',   type=int,               default=1,          help="max permutation depth (careful! massive output)", metavar='INT')
    parser.add_argument('-s',       '--target-size',    type=human_to_bytes,                        help="limit size of output wordlist")


    try:

        options = parser.parse_args()

        # print help if there's nothing to analyze
        if type(options.wordlist) == ReadSTDIN and stdin.isatty():
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
    except (BrokenPipeError, IOError):
        pass
    except KeyboardInterrupt:
        stderr.write("\n[!] Program interrupted.\n")
        exit(2)