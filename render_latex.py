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
    arg_parser.add_argument('--outfile', default=None,
                            help='Output file (overwritten if already present).'
                                 ' Defaults to standard output.')
    arg_parser.add_argument('filename', help='Path to the notation file.')
    args = arg_parser.parse_args()

    fname = args.filename
    try:
        with open(fname, 'r') as f:
            md = f.read()
    except FileNotFoundError:
        print('No such file: %s' % sys.argv[1])
        sys.exit()

    if args.outfile is None:
        outfile = sys.stdout
    else:
        outfile = open(args.outfile, 'w')

    paras = parse(md)
    preamble, output, title_text = render_latex(paras)

    if args.bare:
        print(output, file=outfile)
    else:
        print(r'\documentclass{article}', file=outfile)
        print(r'\usepackage[margin=1in]{geometry}', file=outfile)
        print(r'\usepackage{parskip}', file=outfile)
        print(r'\usepackage{lmodern}', file=outfile)
        print(preamble, file=outfile)
        print(r'\begin{document}', file=outfile)
        print(title_text, file=outfile)
        print(output, file=outfile)
        print(r'\end{document}', file=outfile)
