#!/usr/bin/env python3

# Transliteration table for Sanskrit
# The right-side of the romanization scheme (what is produced in latex) complies with
# https://en.wikipedia.org/wiki/International_Alphabet_of_Sanskrit_Transliteration
# The left-side of the romanization scheme (what is expected in notation) is mostly
# borrowed from: http://www.medieval.org/music/world/carnatic/shyama.html

translit_table = {
# Vowels
    'a': 'a',
    'A': r'\={a}',
    'i': 'i',
    'I': r'\={\i}',
    'u': 'u',
    'U': r'\={u}',
    'R': r'\d{r}',
    'e': 'e',
    'ai': 'ai',
    'o': 'o',
    'ow': 'ow',
    'au': 'au',
    'M': r'\d{m}',
    'H': r'\d{h}',
    '\'': '\'',
# Consonants
    'k': 'k',
    'kh': 'kh',
    'g': 'g',
    'gh': 'gh',
    'HN': r'\.{n}',
    'c': 'c',
    'ch': 'ch',
    'j': 'j',
    'jh': 'jh',
    'Hn': r'\~{n}',
    'T': r'\d{t}',
    'Th': r'\d{t}h',
    'D': r'\d{d}',
    'Dh': r'\d{d}h',
    'N': r'\d{n}',
    't': 't',
    'th': 'th',
    'd': 'd',
    'dh': 'dh',
    'n': 'n',
    'p': 'p',
    'ph': 'ph',
    'b': 'b',
    'bh': 'bh',
    'm': 'm',
    'y': 'y',
    'r': 'r',
    'l': 'l',
    'v': 'v',
    'sh': '\\\'{s}',
    'S': r'\.{s}',
    'Sh': r'\.{s}',
    's': 's',
    'h': 'h',
}
