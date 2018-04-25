# stretcher.py

A highly customizable wordlist mangler which can be trained on an existing wordlist.
It tries to avoid generating "improbable" passwords by preserving the natural entropy of its input.

<br>

### How it works:
##### (Slightly oversimplified, but this is the gist of it)

1. Analyzes wordlist and generates rules based on the treatment of strings and digits.
		For example, "Pass4word!!" would generate two rules:
		1. Append "4word!!"
		2. Prepend "Pass4" and append "!!"
2. Keeps track of commonly occurring rules, strings, and digits in the wordlist
3. Optionally applies leet / cap mutations to aforementioned strings
4. Trims less common occurrences in order to conform to desired crack time
5. Generates passwords (or optionally, hashcat resources) based on combination of gathered lists, mutations, and rules


<br>


### Help:
~~~
usage: stretcher.py [-h] [-w] [-r] [--report-size] [-n] [-hc DIR] [-t] [-p]
                    [-s] [-d] [-g] [-L] [-c] [-C] [-dd] [-P INT]

FETCH THE PASSWORD STRETCHER

optional arguments:
  -h, --help            show this help message and exit
  -w , --wordlist       wordlist to analyze / stretch (default: STDIN)
  -r, --report          print report
  --report-size         maximum number of results in report
  -n, --no-pend         cap/leet mangling only - no appending/prepending
  -hc DIR, --hashcat DIR
                        create hashcat resources in this folder
  -t , --target-time    desired maximum crack time in hours
  -p , --pps            expected hashrate (passwords per second)
  -s , --strings        use these strings instead of those in the wordlist
  -d , --digits         during rule generation, replace digits with these
  -g, --common-digits   during rule generation, replace digits with common
                        occurrences
  -L, --leet            "leetspeak" mutations
  -c, --cap             common upper/lowercase variations
  -C, --capswap         all possible case combinations
  -dd, --double         double each word (e.g. "Pass" --> "PassPass")
  -P INT, --permutations INT
                        Max permutation depth (careful! massive output)
~~~

<br>



### Example #1:
~~~
$ echo -e 'a_few_somewhat\nc0mplex22\nPass.words' | ./stretcher.py
[+] 3 words processed  
words
Pass.words
words.words
words22
a_few_words
a_words_somewhat
words_few_somewhat
Pass
Pass.Pass
Pass.words
Pass22
a_few_Pass
a_Pass_somewhat
Pass_few_somewhat
c0mplex
Pass.c0mplex
c0mplex.words
c0mplex22
a_few_c0mplex
a_c0mplex_somewhat
c0mplex_few_somewhat
somewhat
Pass.somewhat
somewhat.words
somewhat22
a_few_somewhat
a_somewhat_somewhat
somewhat_few_somewhat
few
Pass.few
few.words
few22
a_few_few
a_few_somewhat
few_few_somewhat
a
Pass.a
a.words
a22
a_few_a
a_a_somewhat
a_few_somewhat
~~~

<br>

### Example #2:
~~~
$ head -n 1000000 rockyou.txt | ./stretcher.py --target-time 1 --report
[+] 999,999 words processed  

Top 25 Strings out of 463,571 (2.2% coverage)
===============================================
          1,957 (0.2%):    love                          
          1,649 (0.2%):    life                          
          1,567 (0.2%):    ever                          
          1,339 (0.1%):    may                           
          1,114 (0.1%):    me                            
          1,063 (0.1%):    eva                           
            946 (0.1%):    u                             
            897 (0.1%):    june                          
            765 (0.1%):    july                          
            689 (0.1%):    k                             
            682 (0.1%):    a                             
            651 (0.1%):    sexy                          
            617 (0.1%):    angel                         
            604 (0.1%):    baby                          
            559 (0.1%):    pink                          
            557 (0.1%):    m                             
            554 (0.1%):    i                             
            552 (0.1%):    jan                           
            547 (0.1%):    feb                           
            545 (0.1%):    j                             
            497 (0.1%):    chris                         
            480 (0.1%):    s                             
            456 (0.1%):    dec                           
            446 (0.0%):    c                             
            424 (0.0%):    nov                           

[!] No digits to display.



Top 25 Rules out of 33,146 (46.1% coverage)
=============================================
         54,856 (12.0%):    [string]1                     
         14,922 (3.3%):    [string]123                   
         12,979 (2.8%):    [string]2                     
         10,406 (2.3%):    [string]12                    
          8,563 (1.9%):    [string]3                     
          7,882 (1.7%):    [string]13                    
          7,308 (1.6%):    [string]7                     
          6,574 (1.4%):    [string]11                    
          6,284 (1.4%):    [string]5                     
          5,754 (1.3%):    [string]22                    
          5,724 (1.3%):    [string]23                    
          5,665 (1.2%):    [string]01                    
          5,521 (1.2%):    [string]21                    
          5,496 (1.2%):    [string]07                    
          5,317 (1.2%):    [string]4                     
          5,168 (1.1%):    [string]14                    
          5,075 (1.1%):    [string]10                    
          4,994 (1.1%):    [string]!                     
          4,850 (1.1%):    [string]06                    
          4,712 (1.0%):    [string]08                    
          4,657 (1.0%):    [string]69                    
          4,619 (1.0%):    [string]15                    
          4,392 (1.0%):    [string]8                     
          4,326 (0.9%):    [string]16                    
          4,281 (0.9%):    1[string]                     


Words processed:                                               999,999
Possible combinations:                                  15,365,987,937
Timeframe target:                                        3,600,000,000
Actual combinations:                                     3,600,220,850
======================================================================
Stretched to:                                                   3,600x

Coverage by type:
    words:          94.6% (415,490)
    rules:          94.6% (8,664)

Wordlist size:                                                 45.77GB
Hours at 1,000,000 pps:                                       1.00 hrs
~~~

<br>


### How effective is it?

Pretty darn effective!  Here are a couple of simple examples.  Note that these did not use any of the mutations options such as --leet or --capswap.
<br>
<br>
When used to "stretch" the leaked PHPBB list (which is 184,389 lines long), it was able to crack 1,786,115 passwords from rockyou in under a minute.  That's a 969% increase from the input list.
<br>
Results were similar with the Battlefield list (419,374 lines), which was able to crack 2,253,393 passwords from rockyou.


<br>

#### Notes:
* The output of stretcher.py won't necessarily include all the entries from the wordlist.  The whole point is to generate probable words that AREN'T in the wordlist.</li>
* This tool is a useful option after traditional cracking methods have failed.  Please try and give it plenty of time to do its job.  I recommend specifying a target time, at which point it will inform you how much of the input list it was able to cover in the given timeframe.
* This program attempts to predict the size of its output, but isn't always 100% accurate.  It will play it safe and estimate higher rather than lower, unless --permuatations are used, in which case it doesn't even try.
* I've made an effort to reduce duplicates in output.  A small number of duplicates will occur due to the nature of the algorithm, though.  Linux homies can simply | sort | uniq. ;)</li>
* The difference between --wordlist and --strings: "wordlist" is the list which is analyzed and "learned from".  Commonly occuring strings from that list will be used in the output, but can be overridden with --strings if you want to use your own instead.
* Lots of RAM helps.  Be prepared for memory usage around five times the size of your input wordlist (plus some reasonable headroom for options like --permutations, if included)</li>
* Have a hunch?  Try the --digits or --strings options to inject your predictions into the output.  These options support both comma-separated strings, or a wordlist file.  Try adding --leet and/or --capswap for good measure. Example: `$ cat rockyou.txt | ./stretcher.py --strings evilcorp.txt --leet --digits '2016,2017,2018'`
