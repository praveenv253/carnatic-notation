#!/usr/bin/env python3

from __future__ import print_function, division

import re

from latex_transliteration import latex_sanskrit, latex_sanskrit_capital


def apply_iast_romanization(s, translit_table):
    chars = translit_table.keys()
    simple_chars = [c for c in chars if len(c) == 1]
    compound_chars = [c for c in chars if len(c) > 1]

    # First replace all compound characters, then simple characters
    for c in compound_chars:
        s = re.sub(c, translit_table[c].replace('\\', '\\\\'), s)

    # Then replace all simple characters
    for c in simple_chars:
        s = re.sub(c, translit_table[c].replace('\\', '\\\\'), s)

    return s


def gen_latex_table_text(config):
    """Generate the table environment for latex rendering."""

    if config['cyclesperline'] > 1 and '+' in config['pattern']:
        raise ValueError('Cannot have "+" in pattern when cyclesperline > 1.')

    squeeze = config['squeeze']
    ibs = config['interbeatsep']
    ibs2 = ibs // 2
    for part in config['pattern'].split('+'):
        if 'patternstart' in config:
            col_fmt = config['patternstart']
        else:
            col_fmt = ''

        col_fmt_part = part.replace('_', 'X[%d]' % ibs)
        col_fmt_part = col_fmt_part.replace(',', 'X[10]').replace(';', 'X[10]X[10]')

        if col_fmt_part.startswith('||'):
            col_fmt_part = '##@{}X[%d]' % ibs2 + col_fmt_part[2:]
        elif col_fmt_part.startswith('|'):
            col_fmt_part = '##[white]@{}X[%d]' % ibs2 + col_fmt_part[1:]

        if col_fmt_part.endswith('||'):
            col_fmt_part = col_fmt_part[:-2] + 'X[%d]@{}##' % ibs2
        elif col_fmt_part.endswith('|'):
            col_fmt_part = col_fmt_part[:-1] + 'X[%d]@{}#[white]#' % ibs2

        col_fmt_part = col_fmt_part.replace('||', 'X[%d]@{}##@{}X[%d]' % (ibs2, ibs2))
        col_fmt_part = col_fmt_part.replace('|', 'X[%d]@{}#@{}X[%d]' % (ibs2, ibs2))
        col_fmt_part = col_fmt_part.replace('##', '||').replace('#', '|')

        col_fmt += col_fmt_part * config['cyclesperline']

        # See https://tex.stackexchange.com/a/317543/56690 for top-align
        table_pre = r'\begin{tabu} to %g\linewidth[t]{%s}' % (squeeze, col_fmt)
        table_post = '\end{tabu}'
        num_aksharas = part.count(',') + 2 * part.count(';')

        part_cols = [c for c in part.replace(';', ',,').replace('||', '|') if c in [',', '_', '|']]
        space_pos = []
        j = 0  # Extra inserts produced by | and ||
        for i, c in enumerate(part_cols):
            if c == '_':
                space_pos.append(i + j)
            elif c == '|':
                if i == 0:
                    space_pos.append(i + j)
                elif i == len(part_cols) - 1:
                    space_pos.append(i + j)
                else:
                    space_pos.extend([i+j, i+j+1])
                    j += 1

        yield table_pre, table_post, num_aksharas, space_pos


def extract_swaras(text, config):
    """Extract swaras from text."""

    # Capitalize
    text = text.upper()

    # Add dots above and below for tara sthayi and mandra sthayi swaras
    swaras = []
    for swaram in text.split():
        if any(i in swaram for i in '123'):
            swaram = re.sub(r'([123])', r'\\textsubscript{\1}', swaram)
        if '.' in swaram:
            swaram = re.sub(r'([a-zA-Z])\.', r'\\d{\1}', swaram)
        elif '\'' in swaram:
            swaram = re.sub(r'([a-zA-Z])\'', r'\\.{\1}', swaram)

        swaras.append('\mbox{' + swaram + '}')

    return swaras


def extract_sahityas(text, config):
    """Extract sahityas from text according to config."""

    chunks = text.split()

    if config['iast'] == 'all' or config['iast'] == 'sahityam':
        if config['capitalize'] == 'all' or config['capitalize'] == 'sahityam':
            translit_table = latex_sanskrit_capital
        else:
            translit_table = latex_sanskrit
        sahityas = [apply_iast_romanization(s, translit_table)
                    for s in chunks]
    else:
        sahityas = chunks

    if config['italicize']:
        sahityas = [' ' if s == '_' else r'\textit{' + s + '}' for s in sahityas]
    else:
        sahityas = [' ' if s == '_' else s for s in sahityas]

    sahityas = ['\mbox{' + s + '}' for s in sahityas]

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


def romanize_title_text(text, config):
    if config['iast'] == 'all' or config['iast'] == 'title':
        if config['capitalize'] == 'all' or config['capitalize'] == 'title':
            translit_table = latex_sanskrit_capital
        else:
            translit_table = latex_sanskrit
        text = apply_iast_romanization(text, translit_table)

    return text


def romanize_aro_text(config):
    if config['iast'] == 'all' or config['iast'] == 'title':
        if config['capitalize'] == 'all' or config['capitalize'] == 'title':
            translit_table = latex_sanskrit_capital
            text = 'Aarohanam Avarohanam'
        else:
            translit_table = latex_sanskrit
            text = 'ArOhanam avarOhanam'
        text = apply_iast_romanization(text, translit_table)
    else:
        text = 'Arohanam Avarohanam'

    return text


def romanize_ra_text(config):
    if config['iast'] == 'all' or config['iast'] == 'title':
        if config['capitalize'] == 'all' or config['capitalize'] == 'title':
            translit_table = latex_sanskrit_capital
            text = 'Raagam TaalLam'
        else:
            translit_table = latex_sanskrit
            text = 'rAgam tALam'
        text = apply_iast_romanization(text, translit_table)
    else:
        text = 'Raagam Taalam'

    return text


def render_latex(paras):
    preamble = (r'\usepackage{tabu}' + '\n'
                r'\usepackage{enumitem}' + '\n'
                r'\usepackage{xcolor}' + '\n')
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
                        #swaras.insert(k + kprime, '')
                        swaras.insert(k, '')
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
                            #sahityas.insert(k + kprime, '')
                            sahityas.insert(k, '')
                        output += ' & '.join(sahityas)
                output += '\n' + table_post + '\n\n'
            else:
                output += table_pre + '\n\t'
                chunks_ = chunks[aksh0 : aksh0 + num_aksh]
                for kprime, k in enumerate(space_pos):
                    #chunks_.insert(k + kprime, '')
                    chunks_.insert(k, '')
                output += ' & '.join(chunks_)
                if combo_flag:
                    output += ' \\\\\n\t'
                    sahityas = extract_sahityas(paras[i+1][2], config)
                    sahityas = sahityas[aksh0 : aksh0 + num_aksh]
                    for kprime, k in enumerate(space_pos):
                        #sahityas.insert(k + kprime, '')
                        sahityas.insert(k, '')
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
        title = romanize_title_text(config['title'], config)
        title_text = (r'\begin{center}{\bfseries \Large ' + title
                      + '}\end{center}')
        if 'composer' in config:
            composer = romanize_title_text(config['composer'], config)
            title_text += '\n'
            title_text += (r'\begin{center}\textit{' + composer
                           + '}\end{center}')
        title_text += '\n\n'
        ra_ta_text = romanize_ra_text(config).split()
        if 'raagam' in config and 'taalam' in config:
            raagam = romanize_title_text(config['raagam'], config)
            taalam = romanize_title_text(config['taalam'], config)
            title_text += ('%s: %s \hfill %s: %s'
                           % (ra_ta_text[0], raagam, ra_ta_text[1], taalam))
        elif 'raagam' in config:
            raagam = romanize_title_text(config['raagam'], config)
            title_text += '%s: %s\n\n' % (ra_ta_text[0], raagam)
        elif 'taalam' in config:
            taalam = romanize_title_text(config['taalam'], config)
            title_text += '%s: %s\n\n' % (ra_ta_text[1], taalam)
        if 'arohanam' in config and 'avarohanam' in config:
            title_text += '\\\\'  # Assume at least raagam has been specified
            aro_avaro_text = romanize_aro_text(config).split()
            aro = extract_swaras(config['arohanam'], config)
            avaro = extract_swaras(config['avarohanam'], config)
            title_text += ('%s: %s \hfill %s: %s'
                           % (aro_avaro_text[0], ' '.join(aro),
                              aro_avaro_text[1], ' '.join(avaro) + '\n\n'))

    return preamble, output, title_text
