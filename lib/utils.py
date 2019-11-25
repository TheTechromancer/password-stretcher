#!/usr/bin/env python3

# by TheTechromancer

from sys import stdin


class ReadFile():

    def __init__(self, filename):

        self.filename = str(filename)
        assert(Path(self.filename).is_file()), 'Cannot find the file {}'.format(self.filename)


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



def bytes_to_human(_bytes):

    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
    units = {}
    count = 0
    for size in sizes:
        units[size] = pow(1024, count)
        count +=1

    for size in sizes:
        if abs(_bytes) < 1024.0:
            if size == sizes[0]:
                _bytes = str(int(_bytes))
            else:
                _bytes = '{:.2f}'.format(_bytes)
            return '{}{}'.format(_bytes, size)
        _bytes /= 1024

    raise ValueError