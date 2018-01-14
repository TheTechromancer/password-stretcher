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
			<li>Append "00word!!"/li>
			<li>Prepend "Pass00" and append "!!"</li>
		</ol>
	</li>
	<li>Generates list of common strings &amp; digits</li>
	<li>Outputs passwords (or generates hashcat rules) based on combination of generated lists &amp; rules</li>
	<li>Trims rules and words with lower occurences based on desired crack time</li>
</ol>


<br>


### Help:
~~~
$ ./stretcher.py --help
usage: stretcher.py [-h] [-w] [-r] [-n] [-hc DIR] [-t] [-p] [-s] [-d] [-L]
                    [-c] [-C]

FETCH THE PASSWORD STRETCHER

optional arguments:
  -h, --help            show this help message and exit
  -w , --wordlist       wordlist to analyze / stretch (default: STDIN)
  -r, --report          print report
  -n, --no-pend         mangle only - no appending/prepending
  -hc DIR, --hashcat DIR
                        create hashcat resources in this folder
  -t , --target-time    desired maximum crack time in hours
  -p , --pps            expected hashrate (packets per second)
  -s , --strings        use these strings instead of those in the wordlist
  -d , --digits         use these digits instead of those in the wordlist
  -L, --leet            "leetspeak" mutations
  -c, --cap             common upper/lowercase variations
  -C, --capswap         all possible case combinations
~~~

<br>

### Example:
~~~
$ cat phpbb.txt | ./stretcher.py --target-time 1 --hashcat /tmp/phpbb
[+] 184,389 words processed  

Top 25 Words out of 118,138 (4.9% coverage)
=============================================
            875 (0.5%):    a                             
            597 (0.3%):    b                             
            544 (0.3%):    d                             
            544 (0.3%):    c                             
            486 (0.3%):    k                             
            438 (0.2%):    e                             
            433 (0.2%):    f                             
            426 (0.2%):    phpbb                         
            363 (0.2%):    m                             
            345 (0.2%):    s                             
            315 (0.2%):    p                             
            306 (0.2%):    r                             
            304 (0.2%):    u                             
            302 (0.2%):    n                             
            284 (0.2%):    t                             
            278 (0.2%):    x                             
            246 (0.1%):    h                             
            225 (0.1%):    l                             
            224 (0.1%):    j                             
            223 (0.1%):    g                             
            221 (0.1%):    me                            
            204 (0.1%):    php                           
            186 (0.1%):    z                             
            180 (0.1%):    w                             
            167 (0.1%):    q                             



Top 25 Rules out of 85,778 (24.4% coverage)
=============================================
          5,304 (6.2%):    [string]1                     
          1,936 (2.3%):    [string]123                   
          1,432 (1.7%):    [string]2                     
            993 (1.2%):    [string]12                    
            868 (1.0%):    [string]3                     
            788 (0.9%):    [string]01                    
            719 (0.8%):    [string]7                     
            707 (0.8%):    [string]99                    
            648 (0.8%):    [string]5                     
            638 (0.7%):    [string]11                    
            587 (0.7%):    [string]13                    
            540 (0.6%):    [string]69                    
            533 (0.6%):    [string]4                     
            520 (0.6%):    1[string]                     
            513 (0.6%):    [string]9                     
            488 (0.6%):    [string]0                     
            480 (0.6%):    [string]8                     
            456 (0.5%):    [string]22                    
            443 (0.5%):    [string]00                    
            427 (0.5%):    [string]6                     
            412 (0.5%):    [string]23                    
            390 (0.5%):    [string]1234                  
            388 (0.5%):    [string]21                    
            373 (0.4%):    [string]10                    
            370 (0.4%):    2[string]                     


Words processed:             184,389
Possible combinations:       4,665,650,121
Timeframe target:            3,600,000,000
Actual combinations:         3,600,019,274
=============================================
Overall coverage:            77.16%

Coverage by type:
    words:     93.5%
    rules:     93.5%

[+] Hashcat resources written to /tmp/phpbb
[+] Please run: /tmp/phpbb/hashcat.py -h
~~~

<br>

#### Notes:
<ul>
  <li>I've made an effort to reduce duplicates in output.  A small number of duplicates will occur, though.  Linux homies can simply | sort | uniq. ;)</li>
	<li>Lots of RAM helps.  Be prepared for memory usage around six times the size of your input wordlist (rockyou peaks at approximately 1GB)</li>
</ul>
