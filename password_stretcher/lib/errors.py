#!/usr/bin/env python3

# by TheTechromancer

class PasswordStretcherError(Exception):
    pass

class SpiderError(PasswordStretcherError):
    pass

class InputListError(PasswordStretcherError):
    pass

class PasswordAnalyzerError(PasswordStretcherError):
    pass