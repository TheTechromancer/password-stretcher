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
                yield line.strip(b'\r\n')



class ReadSTDIN():

    def __iter__(self):

        while 1:
            line = stdin.buffer.readline()
            if line:
                yield line.strip(b'\r\n')
            else:
                break