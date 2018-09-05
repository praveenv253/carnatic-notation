#!/usr/bin/env python3

from __future__ import print_function, division

import sys
import argparse

from parser import parse
from latex_renderer import render_latex


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Render notation to latex.')
    arg_parser.add_argument('--bare', action='store_true',
                            help='Output only the notation, without the latex '
                                 'preamble and title formatting.')
    arg_parser.add_argument('filename', help='Path to the notation file')
    args = arg_parser.parse_args()

    fname = args.filename
    try:
        with open(fname, 'r') as f:
            md = f.read()
    except FileNotFoundError:
        print('No such file: %s' % sys.argv[1])
        sys.exit()

    paras = parse(md)
    preamble, output, title_text = render_latex(paras)

    if args.bare:
        print(output)
    else:
        print(r'\documentclass{article}')
        print(r'\usepackage[margin=1in]{geometry}')
        print(r'\usepackage{parskip}')
        print(r'\usepackage{lmodern}')
        print(preamble)
        print(r'\begin{document}')
        print(title_text)
        print(output)
        print(r'\end{document}')
