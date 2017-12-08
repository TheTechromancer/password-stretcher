# password_stretcher
### PASSWORDS, NED!  IN AN OPEN FIEEEELD!!

A wordlist mangler which tries to avoid generating "improbable" passwords by preserving the natural entropy of its input.

Still a work in progress.  In its current state, it only displays informative stats about an analyzed list.

<br>

### How it works:

<ol>
	<li>
		Analyzes wordlist and generates rules based on the treatment of strings and digits.
		For example, "3Passwords!!" would generate two rules:
		<ol>
			<li>Prepend "3" and Append "!!"</li>
			<li>Append "Passwords!!"</li>
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
19,297 processed / 70,702 skipped          

Top 10 string mutations out of 1,490 (57.8% coverage)
=====================================================
  5326:  "__1"
  2698:  "__123"
  993:  "__12"
  761:  "__2"
  505:  "__11"
  451:  "__1234"
  449:  "__01"
  352:  "__7"
  323:  "__13"
  322:  "__3"


Top 10 digit mutations out of 8,446 (3.9% coverage)
===================================================
  114:  "dragon__"
  102:  "qwerty__"
  96:  "password__"
  79:  "monkey__"
  78:  "alex__"
  76:  "daniel__"
  70:  "shadow__"
  70:  "killer__"
  68:  "love__"
  68:  "thomas__"
~~~~

<br>

#### Notes:
<ul>
	<li>When generating rules, overly simple and overly complex words are skipped.  To be precise, words with only one character type (such as "iloveyou") or a complex mask (such as "a1!b2@c3#d4$")</li>
	<li>Be prepared for memory usage up to two times as large as your input wordlist</li>
</ul>