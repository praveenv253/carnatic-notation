#!/usr/bin/env python3

"""
A parser for Carnatic music notation written in markdown. Heavily inspired by
the Carnot engine (https://github.com/srikumarks/carnot).
"""

from __future__ import print_function, division
import sys


taalam_chars = '|,;+_*'
swaram_chars = 'srgmpdnSRGMPDN\'.123 \t,;_\\'
default_config = {
    'squeeze': 1,
    'italicize': True,
    'cyclesperline': 1,
    'iast': 'none',
    'capitalize': 'none',
    'interbeatsep': 10,
    'papersize': 'a4paper',
    'fontsize': 10
}


def parse(md):
    """
    Parse markdown text in the carnot format into python-familiar data
    structures.

    The parse function returns a list of paragraphs. Each paragraph is a
    tuple consisting of the original line number, the paragraph type (text,
    swaram or sahityam), the paragraph text itself, and the configuration using
    which it should be rendered.

    Configurations may change while the document is being parsed. In that case,
    the new configurations will apply to all following lines.
    """

    paras = []
    config = default_config.copy()

    for i, line_ in enumerate(md.split('\n')):
        line = line_.strip()
        if line == '' or line.startswith('#'):     # Empty line or comment
            continue

        if line.startswith('>>'):                  # Text line
            new_para = (i, 'text', line[2:].strip(), config)
        elif '=' in line:                          # Configuration line
            # There may already be old configs used in old paras. Don't
            # overwrite those configs, but use the new config henceforth.
            config = config.copy()
            try:
                partial_config = parse_config(line)
            except ValueError as e:
                print('Error in line %d: %s' % (i, line_))
                print(e)
                sys.exit(1)
            else:
                config.update(partial_config)
            continue
        elif all(c in swaram_chars for c in line):  # Swaram line
            new_para = (i, 'swaram', line, config)
        else:
            new_para = (i, 'sahityam', line, config)

        paras.append(new_para)

    return paras


def sanitize_pattern(pattern):
    pattern = ''.join(pattern.split())  # Remove all spaces in the string

    if any(c not in taalam_chars for c in pattern):
        error_str = ('Invalid character in taalam pattern configuration. '
                     'Valid characters are: %s' % taalam_chars)
        raise ValueError(error_str)

    return pattern


def parse_config(config_line):
    """Parse and validate a configuration line."""

    key, val = config_line.split('=', maxsplit=1)
    key, val = (key.strip(), val.strip())

    partial_config = {}
    if key == 'pattern':
        partial_config[key] = sanitize_pattern(val)
    elif key == 'patternstart':
        partial_config[key] = sanitize_pattern(val)
    elif key == 'squeeze':
        partial_config[key] = float(val)
    elif key in ['cyclesperline', 'interbeatsep', 'fontsize']:
        partial_config[key] = int(val)
    elif key == 'italicize':
        partial_config[key] = (val.lower() == 'true')
    elif key in ['title', 'raagam', 'taalam', 'arohanam', 'avarohanam',
                 'composer', 'iast', 'capitalize', 'papersize']:
        partial_config[key] = val
    else:
        raise ValueError('Unrecognized configuration option %s' % key)

    return partial_config
