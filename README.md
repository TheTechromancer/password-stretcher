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
~~~~
cat rockyou.txt | ./stretcher.py --report
  14,344,000 words processed  

Top 50 Words out of 5,984,751 (5.9% coverage)
===============================================
         61,742 (0.5%):    a                             
         38,242 (0.3%):    m                             
         37,653 (0.3%):    s                             
         37,473 (0.3%):    k                             
         34,860 (0.3%):    j                             
         30,141 (0.2%):    b                             
         28,762 (0.2%):    c                             
         28,511 (0.2%):    com                           
         27,369 (0.2%):    d                             
         22,513 (0.2%):    l                             
         22,450 (0.2%):    e                             
         21,363 (0.2%):    r                             
         21,229 (0.2%):    t                             
         18,878 (0.1%):    n                             
         18,262 (0.1%):    love                          
         17,385 (0.1%):    ever                          
         17,124 (0.1%):    p                             
         16,794 (0.1%):    i                             
         16,715 (0.1%):    g                             
         15,968 (0.1%):    me                            
         15,738 (0.1%):    u                             
         14,687 (0.1%):    h                             
         14,677 (0.1%):    x                             
         14,137 (0.1%):    life                          
         13,642 (0.1%):    eva                           
         12,764 (0.1%):    f                             
         11,212 (0.1%):    y                             
         11,023 (0.1%):    o                             
          9,710 (0.1%):    v                             
          9,076 (0.1%):    w                             
          8,962 (0.1%):    z                             
          7,374 (0.1%):    A                             
          6,544 (0.1%):    baby                          
          6,371 (0.0%):    hotmail                       
          6,332 (0.0%):    may                           
          5,483 (0.0%):    angel                         
          5,423 (0.0%):    q                             
          4,935 (0.0%):    sexy                          
          4,827 (0.0%):    yahoo                         
          4,662 (0.0%):    J                             
          4,628 (0.0%):    L                             
          4,580 (0.0%):    my                            
          4,512 (0.0%):    M                             
          4,297 (0.0%):    alex                          
          4,214 (0.0%):    luv                           
          4,210 (0.0%):    D                             
          4,063 (0.0%):    pink                          
          4,051 (0.0%):    S                             
          4,001 (0.0%):    june                          
          3,914 (0.0%):    sam                           



Top 50 Rules out of 2,081,768 (29.9% coverage)
================================================
        446,736 (5.2%):    [string]1                     
        130,553 (1.5%):    [string]2                     
        103,784 (1.2%):    [string]123                   
         89,797 (1.0%):    [string]3                     
         86,666 (1.0%):    [string]12                    
         73,889 (0.9%):    [string]7                     
         66,573 (0.8%):    [string]13                    
         63,806 (0.7%):    [string]5                     
         60,419 (0.7%):    1[string]                     
         56,558 (0.7%):    [string]4                     
         55,633 (0.6%):    [string]11                    
         51,543 (0.6%):    [string]!                     
         50,542 (0.6%):    [string]22                    
         50,395 (0.6%):    [string]23                    
         50,327 (0.6%):    [string]07                    
         48,984 (0.6%):    [string]01                    
         48,287 (0.6%):    [string]21                    
         47,632 (0.6%):    [string]8                     
         45,735 (0.5%):    [string]14                    
         45,150 (0.5%):    [string]10                    
         44,072 (0.5%):    [string]08                    
         43,809 (0.5%):    [string]6                     
         42,206 (0.5%):    [string]06                    
         41,812 (0.5%):    [string]9                     
         41,809 (0.5%):    [string]15                    
         38,951 (0.5%):    [string]16                    
         38,693 (0.4%):    [string]69                    
         37,673 (0.4%):    [string]18                    
         36,306 (0.4%):    [string]17                    
         33,690 (0.4%):    [string]24                    
         33,256 (0.4%):    [string]05                    
         31,548 (0.4%):    [string]09                    
         30,243 (0.4%):    [string].                     
         28,724 (0.3%):    [string]88                    
         28,188 (0.3%):    [string]19                    
         27,909 (0.3%):    [string]25                    
         27,120 (0.3%):    [string]20                    
         25,758 (0.3%):    [string]0                     
         25,059 (0.3%):    [string]03                    
         23,903 (0.3%):    [string]04                    
         23,770 (0.3%):    [string]27                    
         23,019 (0.3%):    [string]89                    
         23,011 (0.3%):    [string]02                    
         22,527 (0.3%):    [string]99                    
         22,394 (0.3%):    [string]1234                  
         22,083 (0.3%):    [string]101                   
         21,860 (0.3%):    [string]26                    
         21,649 (0.3%):    [string]77                    
         20,885 (0.2%):    [string]28                    
         20,456 (0.2%):    [string]33                    

Total possible combinations: 12,458,863,119,768
~~~~

<br>

#### Notes:
<ul>
	<li>When generating rules, overly simple and overly complex words are skipped.  To be precise, words with only one character type (such as "iloveyou") or a complex mask (such as "a1!b2@c3#d4$")</li>
	<li>Lots of RAM helps.  Be prepared for memory usage around six times the size of your input wordlist (rockyou peaks at approximately 1GB)</li>
</ul>
