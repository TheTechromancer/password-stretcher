# stretcher.py

A password mangler written in Python.  Generate a huge password list from a website, file, or pipe.  Generates capitalization and l33t vARIat1on$ of words.  You can specify the length of the output.

<br>

## Basics:
`stretcher.py` allows you to apply l33t mutations to a list of words without going off the rails of the crazy train.  It prioritizes the most probable mutations and spreads them evenly across all words.  By default, output is set to 100 million words or 1000x times the input, whichever is larger.

<br>

## Usage:
~~~
$ ./stretcher.py --help
usage: stretcher.py [-h] [-i] [-L] [-c] [-C] [-dd] [-P INT] [--limit LIMIT]
                    [--spider-depth SPIDER_DEPTH]

FETCH THE PASSWORD STRETCHER

optional arguments:
  -h, --help            show this help message and exit
  -i , --input          input website or wordlist (default: STDIN)
  -L, --leet            "leetspeak" mutations
  -c, --cap             common upper/lowercase variations
  -C, --capswap         all possible case combinations
  -dd, --double         double each word (e.g. "Pass" --> "PassPass")
  -P INT, --permutations INT
                        max permutation depth (careful! massive output)
  --limit LIMIT         limit length of output (default: max(100M, 1000x
                        input))
  --spider-depth SPIDER_DEPTH
                        maximum website spider depth (default: 1)
~~~

<br>

## Example 1: Create a list of 666,672 passwords (9.01MB) from only three words
~~~
$ echo -e 'normal\nenglish\nwords' | ./stretcher.py --leet --capswap --permutations 2
[+] Reading input wordlist... read 3 words.
[*] Output capped at 393,216,000 words
[+] Mutations allowed per word:
     - leet:           4,047
     - capitalization: 8,095
words
WORDS
Words
w0rds
W0RDS
...
normal
NORMAL
Normal
n0rmal
N0RMAL
...
english
ENGLISH
English
3nglish
3NGLISH
...
englishenglish
englishwords
englishnormal
wordsenglish
wordswords
wordsnormal
normalenglish
normalwords
normalnormal
...
~~~

## Example 2: Create a 10-million-word list from a website
~~~
./stretcher.py -i 'https://wikipedia.org' --leet --limit 10M > wordlist.txt
[+] Spidered 291 pages
[+] Reading input wordlist... read 172,629 words.
[*] Output capped at 10,000,000 words
[+] Mutations allowed per word:
     - leet:           57
[+] 9,792,383 words written (152.36MB)
~~~

## Example 3: Pair with hashcat rules for maximum coverage
~~~
$ echo password | ./stretcher.py --capswap --leet | hashcat -r OneRuleToRuleThemAll.rule ...
~~~

<br>