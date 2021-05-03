# by TheTechromancer

# This was adapted from the Password Statistical Analysis tool by Peter Kacherginsky
# https://github.com/iphelix/pack

class PasswordPolicy:

    charset_choices = ['numeric', 'loweralpha', 'upperalpha', 'special']

    charset_flags = {
        0b0001: 'numeric',
        0b0010: 'loweralpha',
        0b0100: 'upperalpha',
        0b1000: 'special',
        0b0110: 'mixedalpha',
        0b0011: 'loweralphanum',
        0b0101: 'upperalphanum',
        0b1010: 'loweralphaspecial',
        0b1100: 'upperalphaspecial',
        0b1001: 'specialnum',
        0b1110: 'mixedalphaspecial',
        0b1101: 'upperalphaspecialnum',
        0b1011: 'loweralphaspecialnum',
        0b0111: 'mixedalphanum',
        0b1111: 'all',
        'numeric': 0b0001,
        'loweralpha': 0b0010,
        'upperalpha': 0b0100,
        'special': 0b1000
    }

    def __init__(self, minlength=None, maxlength=None, mincharsets=None, required_charsets=None, regex=None):

        self.minlength = minlength
        self.maxlength = maxlength
        self.mincharsets = mincharsets
        self.regex = regex
        self.required_charset = None
        if required_charsets is not None:
            self.required_charset = 0b0000
            for charset in [c.strip().lower() for c in required_charsets]:
                if charset in self.charset_flags:
                    self.required_charset |= self.charset_flags[charset]


    def meets_policy(self, password, pass_length=None, charset=None):

        if type(password) == bytes:
            try:
                password = password.decode()
            except UnicodeError:
                password = str(password)[2:-1]

        #if pass_length is None or charset is None:
        meets_policy, pass_length, charset, num_charsets, simplemask, advancedmask = self.analyze_password(password, calc_policy=False)

        meets_policy = False
        if (self.maxlength is None          or pass_length <= self.maxlength) and \
           (self.minlength is None          or pass_length >= self.minlength) and \
           (self.regex is None              or self.regex.match(password)) and \
           (self.mincharsets is None        or num_charsets >= self.mincharsets) and \
           (self.required_charset is None   or self.required_charset & charset == self.required_charset):
           meets_policy = True
        return meets_policy


    def analyze_password(self, password, calc_policy=True):

        # Character-set flags
        charset = 0b0000
        required_charset = 0b0000
        simplemask = []
        advancedmask_string = []

        # Detect simple and advanced masks
        for letter in password:
 
            if letter.islower():
                charset |= 0b0010
                if calc_policy:
                    advancedmask_string.append('?l')
                    if not simplemask or not simplemask[-1] == 'Word': simplemask.append('Word')

            elif letter.isdigit():
                charset |= 0b0001
                if calc_policy:
                    advancedmask_string.append('?d')
                    if not simplemask or not simplemask[-1] == 'Number': simplemask.append('Number')

            elif letter.isupper():
                charset |= 0b0100
                if calc_policy:
                    advancedmask_string.append('?u')
                    if not simplemask or not simplemask[-1] == 'Word': simplemask.append('Word')

            else:
                charset |= 0b1000
                if calc_policy:
                    advancedmask_string.append('?s')
                    if not simplemask or not simplemask[-1] == 'Symbol': simplemask.append('Symbol')

        num_charsets = bin(charset).count('1')
        pass_length = len(password)
        meets_policy = None
        if calc_policy:
            meets_policy = self.meets_policy(password, pass_length, charset)

        return (
            meets_policy,
            pass_length,
            charset,
            num_charsets,
            '+'.join(simplemask) if len(simplemask) <= 3 else 'Other',
            ''.join(advancedmask_string)
        )


    def wrap(self, iterable):

        if not self:
            yield from iterable

        else:
            for password in iterable:
                if self.meets_policy(password):
                    yield password


    def __bool__(self):

        return not all([_ is None for _ in [self.minlength, self.maxlength, self.mincharsets, self.required_charset, self.regex]])