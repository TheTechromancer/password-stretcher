# password_stretcher

A wordlist mangler which tries to avoid generating "improbable" passwords by preserving the natural entropy of its input.

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
	<li>Trims rules and words with lower occurences based on desired crack time (TODO)</li>
</ol>


<br>

### Basic usage:
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

[+] Hashcat resources written to /tmp/asdf
[+] Please run: /tmp/asdf/hashcat.py -h
~~~

<br>

#### Notes:
<ul>
	<li>When generating rules, overly simple and overly complex words are skipped.  To be precise, words with only one character type (such as "iloveyou") or a complex mask (such as "a1!b2@c3#d4$")</li>
	<li>Lots of RAM helps.  Be prepared for memory usage around six times the size of your input wordlist (rockyou peaks at approximately 1GB)</li>
</ul>
