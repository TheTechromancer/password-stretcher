# stretcher.py

A highly customizable wordlist mangler which can be trained on an existing wordlist.
It tries to avoid generating "improbable" passwords by preserving the natural entropy of its input.

<br>

### How it works:

<ol>
	<li>
		Analyzes wordlist and generates rules based on the treatment of strings and digits.
		For example, "Pass00word!!" would generate two rules:
		<ol>
			<li>Append "00word!!"</li>
			<li>Prepend "Pass00" and append "!!"</li>
		</ol>
	</li>
	<li>Generates list of strings commonly occurring in the wordlist</li>
  <li>Optionally applies leet / cap mutations to said strings</li>
  <li>Trims list entries with lower occurrence to match desired crack time</li>
	<li>Outputs passwords (or optionally generates hashcat rules) based on combination of generated lists, mutations, and rules</li>
</ol>


<br>


### Help:
~~~
usage: stretcher.py [-h] [-w] [-r] [--report-size] [-n] [-hc DIR] [-t] [-p]
                    [-s] [-d] [-g] [-L] [-c] [-C]

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
[+] 1,000,000 words processed  

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


Words processed:                                             1,000,000
Possible combinations:                                  15,365,987,937
Timeframe target:                                        3,600,000,000
Actual combinations:                                     3,600,220,850
======================================================================
Overall coverage:                                               23.43%

Coverage by type:
    words:          94.6% (415,490)
    rules:          94.6% (8,664)

Wordlist size:                                                 45.77GB
Hours at 1,000,000 pps:                                       1.00 hrs
~~~

<br>

#### Notes:
<ul>
  <li>I've made an effort to reduce duplicates in output.  A small number of duplicates will occur due to the nature of the algorithm, though.  Linux homies can simply | sort | uniq. ;)</li>
	<li>Lots of RAM helps.  Be prepared for memory usage around five times the size of your input wordlist (plus some headroom for --cap, if included)</li>
  <li>
    Have a hunch?  Try the --digits or --strings options to inject your predictions into the output.  These options support both comma-separated strings, or a wordlist file.  Try adding --leet and/or --capswap for good measure. Example:
    `$ cat rockyou.txt | ./stretcher.py --strings evilcorp --leet --digits 2016,2017,2018`
  </li>
</ul>
