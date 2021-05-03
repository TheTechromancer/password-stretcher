#!/usr/bin/env python3

# by TheTechromancer

import re
import requests
import urllib.parse
from sys import stderr
from .errors import SpiderError
from .utils import url_to_domain
from html.parser import HTMLParser



class Parser(HTMLParser):
    '''
    Parses HTML data and extracts words
    Keeps count of each word in self.words
    '''

    def __init__(self):

        self.word_regex = re.compile(r'[a-z][a-z01357$@]+[a-z]', re.I)

        # track occurrences of each word
        self.words = dict()
        # stores each responses' links to other pages
        self.temp_links = set()

        super().__init__()


    def injest(self, html):

        self.temp_links.clear()
        self.feed(html)
        self.close()
        self.handle_words(html)
        return list(self.temp_links)


    def handle_words(self, html):

        # strip start tags
        #html = re.sub(r'<\w+', '', html)
        # strip end tags
        #html = re.sub(r'</\w+>', '', html)

        for word in self.word_regex.findall(html):
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

    def __init__(self, url, depth=2, user_agent=None):

        if user_agent is None:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.75'
        self.user_agent = user_agent

        self.url = url
        self.base_domain = url_to_domain(url)
        self.session = requests.Session()
        self.parser = Parser()
        self.visited = set()
        self.depth = depth
        self.headers = {
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9'
        }


    def start(self):

        self.headers.update({'User-Agent': self.user_agent})

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

        if not url in self.visited and depth > 0:

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

        stderr.write(f'\r[+] Found {len(self.parser.words):,} words in {len(self.visited):,} pages')



    def __iter__(self):

        words = list(self.parser.words.items())
        words.sort(key=lambda x: x[1], reverse=True)

        for word, count in words:
            yield word.encode('utf-8')