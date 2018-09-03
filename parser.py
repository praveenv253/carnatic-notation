#!/usr/bin/env python3

"""
A parser for Carnatic music notation written in markdown. Heavily inspired by
the Carnot engine (https://github.com/srikumarks/carnot).
"""

from __future__ import print_function, division
import sys
import re


taalam_chars = '|,;+_'
swaram_chars = 'srgmpdnSRGMPDN\'.123 \t,;'
default_config = {'squeeze': 1, 'italicize': 1, 'cyclesperline': 1}


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

    partial_config = default_config
    if key == 'pattern':
        partial_config[key] = sanitize_pattern(val)
    elif key == 'patternstart':
        partial_config[key] = sanitize_pattern(val)
    elif key == 'squeeze':
        partial_config[key] = float(val)
    elif key == 'cyclesperline':
        partial_config[key] = int(val)
    elif key in ['title', 'raagam', 'taalam', 'arohanam', 'avarohanam',
                 'composer']:
        partial_config[key] = val
    else:
        raise ValueError('Unrecognized configuration option %s' % key)

    return partial_config


def gen_latex_table_text(config):
    """Generate the table environment for latex rendering."""

    if config['cyclesperline'] > 1 and '+' in config['pattern']:
        raise ValueError('Cannot have "+" in pattern when cyclesperline > 1.')

    squeeze = config['squeeze']
    for part in config['pattern'].split('+'):
        if 'patternstart' in config:
            col_fmt = sanitize_pattern(config['patternstart'])
        else:
            col_fmt = ''
        col_fmt += (part.replace('_', 'X[5]').replace(',', 'X[10]').replace(';', 'X[10]X[10]').replace('||', 'X[2]@{}$@{}X[2]').replace('|', 'X[2]@{}|@{}X[2]').replace('$', '||')
                    * config['cyclesperline'])

        # See https://tex.stackexchange.com/a/317543/56690 for top-align
        table_pre = r'\begin{tabu} to %g\textwidth[t]{%s}' % (squeeze, col_fmt)
        table_post = '\end{tabu}'
        num_aksharas = part.count(',') + 2 * part.count(';')

        part_cols = [c for c in part.replace(';', ',,').replace('||', '|') if c in [',', '_', '|']]
        space_pos = []
        for i, c in enumerate(part_cols):
            if c == '_':
                space_pos.append(i)
            elif c == '|':
                space_pos.extend([i-1, i-1])

        yield table_pre, table_post, num_aksharas, space_pos


def extract_swaras(text, config):
    """Extract swaras from text."""

    # Capitalize
    text = text.upper()

    # Add dots above and below for tara sthayi and mandra sthayi swaras
    swaras = []
    for swaram in text.split():
        num = None
        if any(i in swaram for i in '123'):
            num = re.findall(r'\d', swaram)[0]
            swaram = swaram.replace(num, '')
        if '.' in swaram:
            swaram = '\d{%s}' % swaram.replace('.', '')
        elif '\'' in swaram:
            swaram = '\\.{%s}' % swaram.replace('\'', '')
        if num:
            swaram += r'\textsubscript{%s}' % num

        swaras.append(swaram)

    return swaras


def extract_sahityas(text, config):
    """Extract sahityas from text according to config."""

    chunks = text.split()

    if config['italicize']:
        sahityas = [' ' if s == '_' else r'\textit{' + s + '}' for s in chunks]
    else:
        sahityas = [' ' if s == '_' else s for s in chunks]

    return sahityas


def extract_text(text, config):
    """Extract textual elements and apply formatting if any."""

    if not text.startswith('\\'):
        return text + '\n\n'

    cmd_txt = text.split(None, maxsplit=1)
    if len(cmd_txt) == 1:
        cmd = cmd_txt[0]
    else:
        cmd, txt = cmd_txt
    cmd = cmd[1:]  # Remove backslash

    if cmd == 'bold':
        output = r'\textbf{' + txt + '}\n\n'
    elif cmd == 'enum':
        output = r'\begin{enumerate}[label=\arabic*),leftmargin=*]' + '\n'
    elif cmd == 'item':
        output = r'\item'
    elif cmd == 'endenum':
        output = r'\end{enumerate}' + '\n\n'
    elif cmd == 'empty':
        output = '\\ \n\n'
    else:
        raise ValueError('Unknown command \\%s' % cmd)

    return output


def render_latex(paras):
    preamble = (r'\usepackage{tabu}' + '\n'
                r'\usepackage{enumitem}' + '\n')
    output = ''

    i = 0
    while i < len(paras):
        para = paras[i]
        num, kind, text, config = para

        if kind == 'text':
            output += extract_text(text, config)
            i += 1
            continue

        combo_flag = 0
        if (i < len(paras) - 1   # Relying on short-circuiting here
            and kind == 'swaram' and paras[i+1][1] == 'sahityam'
            and paras[i+1][0] == num + 1):
            # If a swaram line is immediately followed by a sahityam line,
            # the they will automatically be rendered in the same table
            combo_flag = 1
            # TODO: When cyclesperline > 1, check this condition for that many
            #       cycles.

        if kind == 'swaram':
            chunks = extract_swaras(text, config)
        elif kind == 'sahityam':
            chunks = extract_sahityas(text, config)

        # TODO: Validate the swaram/sahityam against the taalam config and
        #       cyclesperline before rendering
        # TODO: Test line-splitting within a single taalam cycle
        aksh0 = 0
        for table_params in gen_latex_table_text(config):
            table_pre, table_post, num_aksh, space_pos = table_params
            if config['cyclesperline'] > 1:
                output += table_pre + '\n\t'
                for j in range(config['cyclesperline']):
                    if j > 0:
                        output += ' & '
                    swaras = extract_swaras(paras[i + (1+combo_flag)*j][2],
                                            config) # Config should be the same
                    for kprime, k in enumerate(space_pos):
                        swaras.insert(k + kprime, '')
                    output += ' & '.join(swaras)
                if combo_flag:
                    output += '\\\\\n\t'
                    for j in range(config['cyclesperline']):
                        if j > 0:
                            output += ' & '
                        # Config should be the same
                        sahityas = extract_sahityas(paras[i + (1+combo_flag)*j
                                                          + 1][2], config)
                        for kprime, k in enumerate(space_pos):
                            sahityas.insert(k + kprime, '')
                        output += ' & '.join(sahityas)
                output += '\n' + table_post + '\n\n'
            else:
                output += table_pre + '\n\t'
                chunks_ = chunks[aksh0 : aksh0 + num_aksh]
                for kprime, k in enumerate(space_pos):
                    chunks_.insert(k + kprime, '')
                output += ' & '.join(chunks_)
                if combo_flag:
                    output += ' \\\\\n\t'
                    sahityas = extract_sahityas(paras[i+1][2], config)
                    sahityas = sahityas[aksh0 : aksh0 + num_aksh]
                    for kprime, k in enumerate(space_pos):
                        sahityas.insert(k + kprime, '')
                    output += ' & '.join(sahityas)
                output += '\n' + table_post + '\n\n'
                aksh0 += num_aksh

        if combo_flag:
            i += 2 * config['cyclesperline']
        else:
            i += config['cyclesperline']

    title_text = None
    if 'title' in config:
        # Should not matter which config; very last one should do fine
        title_text = (r'\begin{center}{\bfseries \Large ' + config['title']
                      + '}\end{center}')
        if 'composer' in config:
            title_text += '\n'
            title_text += (r'\begin{center}\textit{' + config['composer']
                           + '}\end{center}')
        title_text += '\n\n'
        if 'raagam' in config and 'taalam' in config:
            title_text += ('Raagam: %s \hfill Taalam: %s'
                           % (config['raagam'], config['taalam']))
        elif 'raagam' in config:
            title_text += 'Raagam: %s\n\n' % config['raagam']
        elif 'taalam' in config:
            title_text += 'Taalam: %s\n\n' % config['taalam']
        if 'arohanam' in config and 'avarohanam' in config:
            title_text += '\\\\'  # Assume at least raagam has been specified
            aro = extract_swaras(config['arohanam'], config)
            avaro = extract_swaras(config['avarohanam'], config)
            title_text += ('Arohanam: %s \hfill Avarohanam: %s'
                           % (' '.join(aro), ' '.join(avaro) + '\n\n'))

    return preamble, output, title_text


if __name__ == '__main__':
    fname = 'saraswati-namostute.md'
    f = open(fname)
    md = f.read()

    paras = parse(md)
    preamble, output, title_text = render_latex(paras)

    print(r'\documentclass{article}')
    print(r'\usepackage[margin=1in]{geometry}')
    print(r'\usepackage{parskip}')
    print(r'\usepackage{lmodern}')
    print(preamble)
    print(r'\begin{document}')
    print(title_text)
    print(output)
    print(r'\end{document}')
