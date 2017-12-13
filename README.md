# password_stretcher

A wordlist mangler which tries to avoid generating "improbable" passwords by preserving the natural entropy of its input.

Still a work in progress.  In its current state, it only displays informative stats about an analyzed list.

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

### Basic usage:
~~~~
cat wordlist | ./stretcher.py --report
99,000 words processed      

Top 10 Words out of 74,946 (1.0% coverage)
============================================
            117 (0.1%):    dragon                        
            115 (0.1%):    qwerty                        
            110 (0.1%):    password                      
             97 (0.1%):    a                             
             89 (0.1%):    love                          
             85 (0.1%):    monkey                        
             83 (0.1%):    shadow                        
             80 (0.1%):    alex                          
             78 (0.1%):    daniel                        
             76 (0.1%):    thomas                        



Top 10 Rules out of 1,768 (56.8% coverage)
============================================
          5,562 (24.6%):    [string]1                     
          2,816 (12.5%):    [string]123                   
          1,057 (4.7%):    [string]12                    
            811 (3.6%):    [string]2                     
            544 (2.4%):    [string]11                    
            487 (2.2%):    [string]01                    
            469 (2.1%):    [string]1234                  
            374 (1.7%):    [string]7                     
            353 (1.6%):    [string]3                     
            352 (1.6%):    [string]13
~~~~

<br>

#### Notes:
<ul>
	<li>When generating rules, overly simple and overly complex words are skipped.  To be precise, words with only one character type (such as "iloveyou") or a complex mask (such as "a1!b2@c3#d4$")</li>
	<li>Be prepared for memory usage up to two times as large as your input wordlist</li>
</ul>
