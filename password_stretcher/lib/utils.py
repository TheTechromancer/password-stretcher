#!/usr/bin/env python3

# by TheTechromancer

import sys
import string
from pathlib import Path
from urllib.parse import urlparse
from .errors import InputListError

# UnicodeDammit
import logging
from bs4 import UnicodeDammit
logging.disable(logging.WARNING)


def read_uris(uris):

    files = []
    for uri in uris:
        if any([uri.startswith(x) for x in ['http://', 'https://']]):
            from .spider import Spider
            return Spider(uri)
        else:
            files.append(uri)

    return ReadFiles(*files)


class ReadFiles():

    def __init__(self, *filenames, binary=True):

        self.files = [ReadFile(filename, binary=binary) for filename in filenames]

    def __iter__(self):

        for file in self.files:
            yield from file


class ReadFile():

    def __init__(self, filename, binary=True):

        self.filename = Path(filename)
        self.binary = binary
        if binary:
            self.mode = 'rb'
            self.strip = b'\r\n'
        else:
            self.mode = 'r'
            self.strip = '\r\n'

        if not self.filename.exists() or self.filename.is_dir():
            raise InputListError(f'Cannot find the file {self.filename}')



    def __iter__(self):

        fucky_errors = 0

        with open(self.filename, self.mode) as f:
            i = f.__iter__()
            while 1:
                try:
                    line = next(i)
                    if not line:
                        break
                    line = line.rstrip(self.strip)
                    if line:
                        yield line
                        fucky_errors = 0
                except StopIteration:
                    break
                except UnicodeDecodeError as e:
                    if fucky_errors > 10000:
                        break
                    for line in UnicodeDammit(e.object).unicode_markup.splitlines()[1:-1]:
                        yield line.rstrip(self.strip)
                        fucky_errors = 0
                    else:
                        fucky_errors += 1



class ReadSTDIN():

    def __init__(self, binary=True):

        if binary:
            self.buffer = sys.stdin.buffer
            self.strip = b'\r\n'
        else:
            self.buffer = sys.stdin
            self.strip = '\r\n'

    def __iter__(self):

        while 1:
            try:
                line = self.buffer.readline()
            except UnicodeDecodeError:
                line = str(sys.stdin.buffer.readline())[2:-1]
            if line:
                line = line.strip(self.strip)
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


def thread_wrapper(target, *args, **kwargs):

    try:
        target(*args, **kwargs)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()