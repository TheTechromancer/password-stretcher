#!/usr/bin/env python3

# by TheTechromancer

import os
import re
import sys
import argparse
from password_stretcher.lib.utils import *
from password_stretcher.lib.errors import *
from password_stretcher.lib.mangler import *
from password_stretcher.lib.spider import Spider
from password_stretcher.lib.policy import PasswordPolicy



def stretcher(options):

    if options.minlength is not None and options.maxlength is not None:
        if options.minlength > options.maxlength:
            print('U WOT M8')
            sys.exit()

    show_written_count = not sys.stdout.isatty()
    written_count = 0

    policy = PasswordPolicy(
        minlength=options.minlength,
        maxlength=options.maxlength,
        mincharsets=options.mincharsets,
        required_charsets=options.charsets,
        regex=options.regex,
    )

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
    if policy:
        sys.stderr.write(f'[+] Filtering based on policy, output size may be reduced\n')

    #sys.stderr.write(f'[+] Estimated output: {len(mangler):,} words\n')

    bytes_written = 0
    for mangled_word in mangler:

        if policy.meets_policy(mangled_word):
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


def main():

    parser = argparse.ArgumentParser(description='FETCH THE PASSWORD STRETCHER')
    parser.add_argument('-i', '--input', nargs='+', default=ReadSTDIN(), help='input website or wordlist(s) (default: STDIN)', metavar='')
    parser.add_argument('--limit', type=human_to_int, help='limit length of output (default: max(100M, 1000x input))')
    mangling = argparse.ArgumentParser.add_argument_group(parser, 'mangling options')
    mangling.add_argument('-L', '--leet', action='store_true', help='"leetspeak" mutations')
    mangling.add_argument('-c', '--cap', action='store_true', help='common upper/lowercase variations')
    mangling.add_argument('-C', '--capswap', action='store_true', help='all possible case combinations')
    mangling.add_argument('-p', '--pend', action='store_true', help='append/prepend common digits & special characters')
    mangling.add_argument('-dd', '--double', action='store_true', help='double each word (e.g. "Pass" --> "PassPass")')
    mangling.add_argument('-P', '--permutations',type=int, default=1, help='max permutation depth (careful! massive output)', metavar='INT')
    filters = argparse.ArgumentParser.add_argument_group(parser, 'password complexity filters')
    filters.add_argument('--minlength', type=int, metavar='8', help='minimum password length')
    filters.add_argument('--maxlength', type=int, metavar='8', help='maximum password length')
    filters.add_argument('--mincharsets', type=int, metavar='3', help='must have this many character sets')
    filters.add_argument('--charsets', nargs='+', choices=PasswordPolicy.charset_choices, help='must include these character sets')
    filters.add_argument('--regex', type=re.compile, metavar='\'$[a-z]*^\'', help='custom regex')
    spidering = argparse.ArgumentParser.add_argument_group(parser, 'spider options')
    spidering.add_argument('--spider-depth', type=int, default=1, help='maximum website spider depth (default: 1)')
    spidering.add_argument('--user-agent', help='user-agent for web spider')

    try:

        options = parser.parse_args()

        # print help if there's nothing to stretch
        if type(options.input) == ReadSTDIN and sys.stdin.isatty():
            parser.print_help()
            sys.stderr.write('\n\n[!] Please specify wordlist(s) or pipe to STDIN\n')
            exit(2)

        if not type(options.input) == ReadSTDIN:
            options.input = read_uris(options.input)

        if type(options.input) == Spider:
            spider = options.input
            spider.depth = options.spider_depth
            spider.user_agent = options.user_agent
            spider.start()

        stretcher(options)


    except re.error:
        print(f'[!] Invalid regex')
        print('[*] Remember to place regex in single quotes: \'^Password[0-9]+\'')
        sys.exit(2)
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
    except (PasswordStretcherError, AssertionError) as e:
        sys.stderr.write(f'\n[!] {e}\n')
        exit(1)
    except argparse.ArgumentError:
        sys.stderr.write('\n[!] Check your syntax. Use -h for help.\n')
        exit(2)
    except KeyboardInterrupt:
        sys.stderr.write('\n[!] Interrupted.\n')
        exit(2)


if __name__ == '__main__':
    main()