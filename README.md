# password_stretcher

A wordlist mangler which tries to avoid generating "improbable" passwords by preserving the natural entropy of its input.

Still a work in progress.  In its current state, it only displays informative stats about an analyzed list.

<br>

### How it works:

<ol>
	<li>
		Analyzes wordlist and generates rules based on the treatment of strings and digits.
		For example, "3Passwords!!" would generate two rules:
		<ol>
			<li>Prepend "3" and Append "!!" to all strings</li>
			<li>Append "Passwords!!" to all digits</li>
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
184,000 words processed      

Top 10 Words out of 129,569 (2.9% coverage)
=============================================
            875 (0.5%):    a                             
            597 (0.3%):    b                             
            544 (0.3%):    c                             
            544 (0.3%):    d                             
            486 (0.3%):    k                             
            438 (0.2%):    e                             
            433 (0.2%):    f                             
            426 (0.2%):    phpbb                         
            363 (0.2%):    m                             
            345 (0.2%):    s                             


Top 10 Rules out of 37,537 (16.1% coverage)
=============================================
          5,304 (6.1%):    [string]1                     
          1,936 (2.2%):    [string]123                   
          1,432 (1.6%):    [string]2                     
            993 (1.1%):    [string]12                    
            868 (1.0%):    [string]3                     
            788 (0.9%):    [string]01                    
            719 (0.8%):    [string]7                     
            707 (0.8%):    [string]99                    
            648 (0.7%):    [string]5                     
            638 (0.7%):    [string]11
~~~~

<br>

#### Notes:
<ul>
	<li>When generating rules, overly simple and overly complex words are skipped.  To be precise, words with only one character type (such as "iloveyou") or a complex mask (such as "a1!b2@c3#d4$")</li>
	<li>Be prepared for memory usage up to two times as large as your input wordlist</li>
</ul>
