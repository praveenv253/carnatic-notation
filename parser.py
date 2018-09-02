#!/usr/bin/env python3

"""
A parser for Carnatic music notation written in markdown. Heavily inspired by
the Carnot engine (https://github.com/srikumarks/carnot).
"""

from __future__ import print_function, division
import sys


taalam_chars = '|,;+'
swaram_chars = 'srgmpdnSRGMPDN\'.123 \t,;'
default_config = {'squeeze': 1}


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
    config = {}

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
                sys.exit()
            else:
                config.update(partial_config)
            continue
        elif all(c in swaram_chars for c in line):  # Swaram line
            new_para = (i, 'swaram', line, config)
        else:
            new_para = (i, 'sahityam', line, config)

        paras.append(new_para)

    return paras


def parse_config(config_line):
    """Parse and validate a configuration line."""

    key, val = config_line.split('=', maxsplit=1)
    key, val = (key.strip(), val.strip())

    partial_config = default_config
    if key == 'taalam':
        val = ''.join(val.split())  # Remove all spaces in the string
        if any(c not in taalam_chars for c in val):
            error_str = ('Invalid character in taalam configuration. '
                         'Valid characters are: %s' % taalam_chars)
            raise ValueError(error_str)
        partial_config[key] = val
        #partial_config['num_aksharas'] = val.count(',') + 2 * val.count(';')
    elif key == 'squeeze':
        partial_config[key] = float(val)
    else:
        raise ValueError('Unrecognized configuration option %s' % key)

    return partial_config


def gen_latex_table_text(config):
    """Generate the table environment for latex rendering."""

    squeeze = config['squeeze']
    for part in config['taalam'].split('+'):
        col_fmt = part.replace(',', 'Y').replace(';', 'YY')
        table_pre = r'\begin{tabularx}{%g\textwidth}{%s}' % (squeeze, col_fmt)
        table_post = '\end{tabularx}'
        num_aksharas = col_fmt.count('Y')
        yield table_pre, table_post, num_aksharas


def render_latex(paras):
    preamble = (r'\usepackage{tabularx}' + '\n'
                r'\newcolumntype{Y}{>{\centering\arraybackslash}X}')
    output = ''

    i = 0
    while i < len(paras):
        para = paras[i]
        num, kind, text, config = para

        if kind == 'text':
            output += text + '\n\n'
            i += 1
            continue

        combo_flag = 0
        if (i < len(paras) - 1   # Relying on short-circuiting here
            and kind == 'swaram' and paras[i+1][1] == 'sahityam'
            and paras[i+1][0] == num + 1):
            # If a swaram line is immediately followed by a sahityam line,
            # the they will automatically be rendered in the same table
            combo_flag = 1

        # Ideally, we should validate the swaram/sahityam against the taalam
        # config before rendering
        aksh0 = 0
        for table_pre, table_post, num_aksh in gen_latex_table_text(config):
            if kind == 'swaram':
                text = text.upper()
                chunks = []
                for chunk in text.split():
                    if '.' in chunk:
                        chunk = '\d{%s}' % chunk.replace('.', '')
                    elif '\'' in chunk:
                        chunk = '\\.{%s}' % chunk.replace('\'', '')
                    chunks.append(chunk)
                text = ' '.join(chunks)

            output += table_pre + '\n'
            output += '\t' + ' & '.join(text.split()[aksh0 : aksh0 + num_aksh])
            if combo_flag:
                output += ' \\\\\n'
                sahityas = paras[i+1][2].split()[aksh0 : aksh0 + num_aksh]
                output += '\t' + ' & '.join(sahityas)
            output += '\n' + table_post + '\n\n'
            aksh0 += num_aksh

        if combo_flag:
            i += 2
        else:
            i += 1

    return preamble, output


if __name__ == '__main__':
    fname = 'saraswati-namostute.md'
    f = open(fname)
    md = f.read()

    paras = parse(md)
    preamble, output = render_latex(paras)

    print(r'\documentclass{article}')
    print(r'\usepackage[margin=1in]{geometry}')
    print(r'\usepackage{parskip}')
    print(r'\usepackage{lmodern}')
    print(preamble)
    print(r'\begin{document}')
    print(output)
    print(r'\end{document}')
