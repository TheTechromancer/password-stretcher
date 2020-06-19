#!/usr/bin/env python3

# by TheTechromancer

import os
from pathlib import Path
from .mutator import Mutator


class Pend(Mutator):

    scale = 5
    fname = 'append/prepend'

    def __init__(self, _input, limit=2048):

        self.rules = []
        self.read_rules()

        super().__init__(_input, limit)


    def __len__(self):

        return min(self.limit, len(self.rules))


    def mutate(self, word):

        yield word

        for rule in self.rules:
            yield rule.replace(b'\x00', word)


    def read_rules(self, rule_dir=None):

        if rule_dir is None:
            rule_dir = Path(__file__).resolve().parent.parent / 'lists'

        for _, _, files in os.walk(rule_dir):
            for file in files:
                if any(file.lower().endswith(x) for x in ['rule', 'rules']):
                    with open(rule_dir / file) as f:
                        lines = [l.strip('\r\n') for l in f.readlines()]
                        for line in lines:
                            try:
                                rule = self.parse_rule(line)
                                if len(rule) > 1:
                                    self.rules.append(rule)
                            except ValueError:
                                continue


    @staticmethod
    def parse_rule(rule):

        parsed_rule = []

        rule_chars = rule.split(' ')
        for char in rule_chars:
            if char.startswith('^'):
                if len(char) == 1:
                    parsed_rule.append(b' ')
                elif len(char) > 1:
                    parsed_rule.append(char[-1].encode('utf-8'))
                else:
                    raise ValueError

        # the word goes here
        parsed_rule.append(b'\x00')

        for char in rule_chars:
            if char.startswith('$'):
                if len(char) == 1:
                    parsed_rule.append(b' ')
                elif len(char) > 1:
                    parsed_rule.append(char[-1].encode('utf-8'))
                else:
                    raise ValueError

        return b''.join(parsed_rule)

