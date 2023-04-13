#!/usr/bin/env python3
import sys
import argparse


class termcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


SEP = '____'


def indent_level(s):
    i = 0
    while s[i] == '\t':
        i += 1
    return i


def make_chs(ilevels):
    chs = {-1: []}
    prs = []
    last_ilevel = {-1: -1}
    for idx, ilevel in enumerate(ilevels):
        chs[idx] = []
        prs.append(last_ilevel[ilevel - 1])
        chs[prs[idx]].append(idx)
        last_ilevel[ilevel] = idx
    return chs, prs


def main():
    global infile, COMMENT
    lines = infile.read().splitlines()
    # filter out comments and empty lines
    lines = [l for l in lines if not l.lstrip().startswith(COMMENT) and l.strip() != '']
    chs, prs = make_chs([indent_level(line) for line in lines])
    # sanity check
    for lineno in range(len(lines)):
        if lines[lineno].endswith(':'):
            if not all(lines[chlineno][-1] in ':.' for chlineno in chs[lineno]):
                print(termcolors.WARNING + termcolors.BOLD, end='')
                print('Potential invalid cmdgrp specification:')
                print(
                    f'All children of intermediate command `{lines[lineno].strip()}` must end with a period or a colon'
                )
                print(termcolors.ENDC, end='')
    # generate output script
    for rootline in chs[-1]:
        if lines[rootline] == '@init.':
            make_init(lines, chs, prs, rootline)
        else:
            recursive_make(lines, chs, prs, rootline)
    outfile.write(f'echo "sourced. root commands:"\n')
    for rootline in chs[-1]:
        outfile.write(f'echo "  {lines[rootline][:-1]}"\n')


def make_interm(fnname, fnchs):
    global outfile
    outfile.write(f'{fnname}() {{')
    outfile.write(f'\n\tcase $1 in')
    for fnch in fnchs:
        outfile.write(f'\n\t\t"{fnch}")')
        outfile.write(f'\n\t\t\tshift 1')
        outfile.write(f'\n\t\t\t{fnname}{SEP}{fnch} $@')
        outfile.write(f'\n\t\t\t;;')
    outfile.write(f'\n\t\t*)')
    outfile.write(
        f'\n\t\t\techo "Invalid argument $1 for \`{fnname.replace(SEP, " ")}\`"'
    )
    outfile.write(f'\n\t\t\techo "available choices:"')
    for fnch in fnchs:
        outfile.write(f'\n\t\t\techo "\t{fnch}"')
    outfile.write(f'\n\t\t\t;;')
    outfile.write(f'\n\tesac')
    outfile.write(f'\n}}\n\n\n')


def make_term(fnname, lines):
    outfile.write(f'{fnname}() {{')
    outfile.write('\n\t'.join([''] + lines))
    outfile.write(f'\n}}\n\n\n')


def recursive_make(lines, chs, prs, lineno):
    if lines[lineno].endswith(':'):
        # descend into children commands
        fnname = name_chain(lines, prs, lineno)
        chlinenos = chs[lineno]
        fnchs = [lines[chlineno].strip()[:-1] for chlineno in chlinenos]
        make_interm(fnname, fnchs)
        for chlineno in chlinenos:
            recursive_make(lines, chs, prs, chlineno)
    elif lines[lineno].endswith('.'):
        # this is a leaf command
        fnname = name_chain(lines, prs, lineno)
        make_term(fnname, [lines[i].strip() for i in chs[lineno]])


def make_init(lines, chs, prs, lineno):
    chlines = [lines[chlineno].strip() for chlineno in chs[lineno]]
    outfile.write('\n'.join([''] + chlines))
    outfile.write(f'\n\n\n')


def name_chain(lines, prs, lineno):
    s = []
    while lineno != -1:
        s.append(lines[lineno].strip()[:-1])
        lineno = prs[lineno]
    s.reverse()
    res = SEP.join(s)
    assert res.isidentifier()
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MiniDecaf compiler')
    parser.add_argument(
        '-i',
        '--infile',
        type=argparse.FileType('r'),
        default='-',
        help='input specification',
    )
    parser.add_argument(
        '-o',
        '--outfile',
        type=argparse.FileType('w'),
        default='-',
        help='file name for output script',
    )
    parser.add_argument(
        '-c', '--comment', type=str, default='----', help='prefix of comment lines'
    )
    args = parser.parse_args()

    global infile, outfile, COMMENT
    infile = args.infile
    outfile = args.outfile
    COMMENT = args.comment
    outfile.write('#!/bin/bash\n\n')
    main()
    print(f'Done.\nUse `source {outfile.name}` to load script.')
