#!/usr/bin/env python3

# by TheTechromancer

import re
import requests
import urllib.parse
from sys import stderr
from .utils import url_to_domain
from .errors import SpiderError
from html.parser import HTMLParser



class Parser(HTMLParser):
    '''
    Parses HTML data and extracts words
    Keeps count of each word in self.words
    '''

    words = dict()
    word_regex = re.compile(r'\w{3,30}')
    # stores each responses' links to other pages
    temp_links = set()


    def injest(self, html):

        self.temp_links.clear()
        self.feed(html)
        self.close()
        self.handle_words(html)
        return list(self.temp_links)


    def handle_words(self, data):

        for word in self.word_regex.findall(data):
            try:
                self.words[word] += 1
            except KeyError:
                self.words[word] = 1

    '''
    def unknown_decl(self, data):

        self.handle_words(data)


    def handle_data(self, data):
        
        self.handle_words(data)


    def handle_comments(self, data):

        self.handle_words(data)
    '''

    def handle_starttag(self, tag, attrs):

        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value:
                    self.temp_links.add(value)




class Spider:

    def __init__(self, url, depth=2):

        self.url = url
        self.base_domain = url_to_domain(url)
        self.session = requests.Session()
        self.parser = Parser()
        self.visited = set()
        self.depth = depth
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/75.0.3770.90 Chrome/75.0.3770.90 Safari/537.36',
        }


    def start(self):

        try:
            self.get(self.url)
            stderr.write('\n')
            stderr.flush()
        except requests.RequestException:
            raise SpiderError(f'Error visiting URL: "{self.url}"')
        except KeyboardInterrupt:
            stderr.write('\n\n[!] Stopping spider...\n')


    def get(self, url, depth=None):

        if depth is None:
            depth = self.depth

        if not url in self.visited and depth >= 0:

            response = self.session.get(url, headers=self.headers)
            self.visited.add(url)
            links = self.parser.injest(response.text)

            for link in links:
                link = urllib.parse.urljoin(url, link)
                try:
                    if url_to_domain(link) == self.base_domain:
                        self.get(link, depth=depth-1)
                except ValueError:
                    continue

        stderr.write(f'\r[+] Spidered {len(self.visited):,} pages')



    def __iter__(self):

        words = list(self.parser.words.items())
        words.sort(key=lambda x: x[1], reverse=True)

        for word, count in words:
            yield word.encode('utf-8')