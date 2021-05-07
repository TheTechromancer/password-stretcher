![password-stretcher](https://user-images.githubusercontent.com/20261699/117364575-14a5d980-ae8c-11eb-815d-32827cc5297b.png)

**Generate disgusting quantities of passwords from websites, files, or stdin.** Compliments [password-smelter](https://github.com/thetechromancer/password-smelter).

## Installation
~~~
$ pip install password-stretcher
~~~

## Basics:
`password-stretcher` allows you to apply mutations to a list of words.  It prioritizes the most probable transforms and spreads them evenly across all input.  By default, output is set to 100 million words or 1000x times the input, whichever is larger.

### Aren't hashcat rules better?
Hashcat rules are great for quickly covering the most probable mutations of a password. `password-stretcher` can cover them all. This is useful if you KNOW or HEAVILY SUSPECT that the password is a variation of a specific word or list of words, but you haven't been able to crack it using hashcat rules.

When enabling `--leet` or `--capswap` mutations, you can be sure that `password-stretcher` will generate **100%** coverage. Even when you `--limit` the results, it will prioritize the most probable ones. Here, you can see that enabling both `--leet` and `--capswap` on a single word ("pass") results in 96 mutations:
~~~
$ echo pass | password-stretcher --leet --capswap | wc -l
[+] Reading input wordlist... read 1 words 
[*] Output capped at 100,000,000 words
[+] Mutations allowed per word:
       leet            7,071
       capitalization  14,142
[+] 96 words written (480B)    
96
~~~
**However,** when we `--limit` the results, only the most common mutations are chosen:
~~~
$ echo pass | password-stretcher --leet --capswap --limit 10
[+] Reading input wordlist... read 1 words 
[*] Output capped at 10 words
[+] Mutations allowed per word:
       leet            2
       capitalization  4
pass
PASS
Pass
pAss
p@ss
P@SS
P@ss
P@Ss
~~~

<br>

## Example 1: Generate 10 million passwords from three words
~~~
$ echo -e 'normal\nenglish\nwords' | password-stretcher --leet --capswap --permutations 2 --limit 10M
[+] Reading input wordlist... read 3 words 
[*] Input wordlist after permutations: 12
[+] Mutations allowed per word:
       leet            645
       capitalization  1,290
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

## Example 2: Generate 10 million passwords from a website
~~~
$ password-stretcher -i 'https://wikipedia.org' --leet --limit 10M > wordlist.txt
[+] Spidered 291 pages
[+] Reading input wordlist... read 172,629 words.
[*] Output capped at 10,000,000 words
[+] Mutations allowed per word:
     - leet:           57
[+] 9,792,383 words written (152.36MB)
~~~

## Example 3: Generate passwords from a codebase
~~~
$ egrep -h -RIio '\b[a-z]+\b' 2>/dev/null | password-stretcher --cap > wordlist.txt
~~~

## Example 4: Pair with hashcat rules because yes
~~~
$ echo password | password-stretcher --capswap --leet | hashcat -r OneRuleToRuleThemAll.rule ...
~~~

## Usage:
~~~
$ password-stretcher --help
usage: password-stretcher [-h] [-i  [...]] [--limit LIMIT] [-L] [-c] [-C] [-p] [-dd] [-P INT] [--minlength 8] [--maxlength 8] [--mincharsets 3]
                          [--charsets {numeric,loweralpha,upperalpha,special} [{numeric,loweralpha,upperalpha,special} ...]] [--regex '$[a-z]*^'] [--spider-depth SPIDER_DEPTH]
                          [--user-agent USER_AGENT]

FETCH THE PASSWORD STRETCHER

optional arguments:
  -h, --help            show this help message and exit
  -i  [ ...], --input  [ ...]
                        input website or wordlist(s) (default: STDIN)
  --limit LIMIT         limit length of output (default: max(100M, 1000x input))

mangling options:
  -L, --leet            "leetspeak" mutations
  -c, --cap             common upper/lowercase variations
  -C, --capswap         all possible case combinations
  -p, --pend            append/prepend common digits & special characters
  -dd, --double         double each word (e.g. "Pass" --> "PassPass")
  -P INT, --permutations INT
                        max permutation depth (careful! massive output)

password complexity filters:
  --minlength 8         minimum password length
  --maxlength 8         maximum password length
  --mincharsets 3       must have this many character sets
  --charsets {numeric,loweralpha,upperalpha,special} [{numeric,loweralpha,upperalpha,special} ...]
                        must include these character sets
  --regex '$[a-z]*^'    custom regex

spider options:
  --spider-depth SPIDER_DEPTH
                        maximum website spider depth (default: 1)
  --user-agent USER_AGENT
                        user-agent for web spider
~~~