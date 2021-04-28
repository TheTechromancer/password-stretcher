#!/usr/bin/env python3

# by TheTechromancer

import string
from sys import stdin
from pathlib import Path
from urllib.parse import urlparse
from .errors import InputListError


def read_uri(uri):

    if any(uri.startswith(x) for x in ['http://', 'https://']):
        from .spider import Spider
        return Spider(uri)
    else:
        return ReadFile(uri)


class ReadFile():

    def __init__(self, filename):

        self.filename = str(filename)

        if not Path(self.filename).is_file():
            raise InputListError(f'Cannot find the file {self.filename}.  use "https://", for website')



    def __iter__(self):

        with open(self.filename, 'rb') as f:
            for line in f:
                line = line.strip(b'\r\n')
                if line:
                    yield line



class ReadSTDIN():

    def __iter__(self):

        while 1:
            line = stdin.buffer.readline()
            if line:
                line = line.strip(b'\r\n')
                if line:
                    yield line
            else:
                break



def int_to_human(i):
    '''
    shortens large integer to human-readable format
    e.g. 1000 --> 1K
    '''

    sizes = ['', 'K', 'M', 'B', 'T']
    units = {}
    count = 0
    for size in sizes:
        units[size] = pow(1000, count)
        count +=1

    for size in sizes:
        if abs(i) < 1000.0:
            if size == sizes[0]:
                i = str(int(i))
            else:
                i = '{:.2f}'.format(i)
            return '{}{}'.format(i, size)
        i /= 1000

    raise ValueError


def human_to_int(h):
    '''
    converts human-readable number to integer
    e.g. 1K --> 1000
    '''

    if type(h) == int:
        return h

    units = {'': 1, 'K': 1000, 'M': 1000**2, 'B': 1000**3, 'T': 1000**4}

    try:
        h = h.upper().strip()
        i = float(''.join(c for c in h if c in string.digits + '.'))
        unit = ''.join([c for c in h if c in string.ascii_uppercase])
    except (ValueError, KeyError):
        raise ValueError(f'Invalid number "{h}"')

    return int(i * units[unit])


def bytes_to_human(_bytes):
    '''
    converts bytes to human-readable filesize
    e.g. 1024 --> 1KB
    '''

    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
    units = {}
    for count,size in enumerate(sizes):
        units[size] = pow(1024, count)

    for size in sizes:
        if abs(_bytes) < 1024.0:
            if size == sizes[0]:
                _bytes = str(int(_bytes))
            else:
                _bytes = '{:.2f}'.format(_bytes)
            return '{}{}'.format(_bytes, size)
        _bytes /= 1024

    raise ValueError



def hostname_to_domain(hostname):

    hostname = hostname.lower().split('.')
    try:
        if hostname[-2] == 'co':
            return '.'.join(hostname[-3:])
        else:
            return '.'.join(hostname[-2:])
    except IndexError:
        return '.'.join(hostname)



def url_to_domain(url):

    try:
        return hostname_to_domain(urlparse(url).hostname).lower()
    except AttributeError:
        raise ValueError(f'Invalid URL: {url}')