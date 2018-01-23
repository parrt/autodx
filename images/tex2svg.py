#!/usr/bin/env python3

# I got it here: https://gist.github.com/W4RH4WK/14c42596de935af6d009

""" Convert LaTeX to SVG

This script will read LaTeX from stdin into a temporary file, compile it,
convert it to SVG and write it to stdout. Temporary files are removed upon
success.

Usage: ./tex2svg [template]

    This script takes one optional parameter, a LaTeX template. All occurences
    of `%BODY%` will be replaced with the data read from stdin.

Requires:
    - XeTeX
    - pdf2svg
    - pdfcrop
"""

import os
import sys
import shutil

from tempfile import mkdtemp
from subprocess import check_call, CalledProcessError

__author__ = 'Alex Hirsch'

# parrt tweaked some of this

TPL = r"""\documentclass[xetex,fontsize=12pt]{scrartcl}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{%FONT%}
\begin{document}
\thispagestyle{empty}
%BODY%
\end{document}
"""


def main(argv):
    tpl = TPL
    font = 'lmodern'
    i = 1
    if len(argv)>1 and argv[i]=='-font':
        i += 1
        font = argv[i]
        i += 1

    cwd = os.getcwd()
    tmp = mkdtemp(prefix='tex2svg_')
    #print(tmp)
    os.chdir(tmp)

    tpl = tpl.replace('%BODY%', sys.stdin.read())
    tpl = tpl.replace('%FONT%', font)
    with open('temp.tex', 'w') as ftex:
        ftex.write(tpl)

    cmds = [['xelatex', '-shell-escape', 'temp.tex'],
            ['pdfcrop', 'temp.pdf'],
            ['pdf2svg', 'temp-crop.pdf', 'temp.svg']]

    log_path = os.path.join(tmp, 'output.log')

    try:
        with open(log_path, 'w') as flog:
            for cmd in cmds:
                check_call(cmd, stdout=flog, stderr=flog)
    except CalledProcessError:
        print('{}: An error occured, check {}'.format(argv[0], log_path),
              file=sys.stderr)
        return -1

    with open('temp.svg', 'r') as fsvg:
        shutil.copyfileobj(fsvg, sys.stdout)

    os.chdir(cwd)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
