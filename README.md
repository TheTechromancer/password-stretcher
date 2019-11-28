# stretcher.py

A wordlist mangler which generates l33t vARIat1on$ of words, with the option to specify the length of the output list.  Written in Python 3.

<br>

## Basics:
`stretcher.py` allows you to apply l33t mutations to a wordlist without going off the rails of the crazy train.  It spreads evenly across all words and puts more likely mutations first.  By default, output is set to 100 million words or 1000x times the input, whichever is larger.

<br>

## Usage:
~~~
$ ./stretcher.py --help
usage: stretcher.py [-h] [-i] [-L] [-c] [-C] [-dd] [-P INT] [--limit LIMIT]

FETCH THE PASSWORD STRETCHER

optional arguments:
  -h, --help            show this help message and exit
  -i , --input          wordlist to stretch (default: STDIN)
  -L, --leet            "leetspeak" mutations
  -c, --cap             common upper/lowercase variations
  -C, --capswap         all possible case combinations
  -dd, --double         double each word (e.g. "Pass" --> "PassPass")
  -P INT, --permutations INT
                        max permutation depth (careful! massive output)
  --limit LIMIT         limit length of output (default: max(100M, 1000x input))
~~~

<br>

## Example: quickly create a large wordlist from only a few words
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

## Example: Create a 1GB wordlist from a website with CeWL
~~~
$ cewl blacklanternsecurity.com | ./stretcher.py --leet --capswap --limit 1M > bls.txt
[+] Reading input wordlist... read 1,338 words.
[*] Output capped at 1,000,000 words
[+] Mutations allowed per word:
     - leet:           186
     - capitalization: 6
[+] 988,808 words written (13.25MB)
~~~

## Tip: pair with hashcat rules for maximum coverage
~~~
$ echo password | ./stretcher.py --capswap --leet | hashcat -r OneRuleToRuleThemAll.rule ...
~~~

<br>