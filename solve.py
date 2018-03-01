#!/usr/bin/env pypy
import argparse
import random
import glob
from collections import namedtuple

Ride = namedtuple('Ride', ['i', 'p_s', 'p_f', 't_s', 't_f'])


def parse(inp):
    # TODO: implement
    itr = (map(int, li.split()) for li in inp.split('\n'))
    R, C, F, N, B, T = next(itr)
    rides = [Ride(i, (a, b), (x, y), s, f) for i, (a, b, x, y, s, f) in enumerate(itr)]

    return argparse.Namespace(B=B, T=T, rides=rides, itr=itr, C=C, R=R, N=N, F=F)


def solve(seed, inp, log):
    # TODO: Solve the problem
    random.seed(seed)
    ns = parse(inp)
    B, T, rides, itr, C, R, N, F = ns.B, ns.T, ns.rides, ns.itr, ns.C, ns.R, ns.N, ns.F
    
    assert (B, T, rides, itr, C, R, N, F) == (ns.B, ns.T, ns.rides, ns.itr, ns.C, ns.R, ns.N, ns.F)

    return '0'


def show(out):
    # TODO: Print the solution here
    print(out)


def score(inp, out):
    # TODO: implement

    if __name__ == '__main__' and args.s:
        show(out)

    return 0


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('inp', nargs='?')
    parser.add_argument('ans', nargs='?')
    parser.add_argument('-s', action='store_true', help="show")
    return parser.parse_args()


def ans2in(ans):
    return ans.replace('.ans', '.in').replace('submission/', 'in/')


def in2ans(inp):
    return inp.replace('.in', '.ans').replace('in/', 'submission/')


if __name__ == '__main__':
    args = get_args()
    if not args or (not args.inp and not args.ans):
        files = []
        for ans in glob.glob('submission/*.ans'):
            files.append((ans2in(ans), ans))
    else:
        if not args.ans:
            if '.ans' in args.inp:
                args.ans = args.inp
                args.inp = ans2in(args.ans)
            elif '.in' in args.inp:
                args.ans = in2ans(args.inp)
            else:
                args.inp = args.inp.replace('.max', '')
                args.ans = 'submission/' + args.inp + '.ans'
                args.inp = 'in/' + args.inp + '.in'
        files = [(args.inp, args.ans)]

    for inpf, ansf in files:
        with open(inpf, 'r') as f:
            inp = f.read()
        with open(ansf, 'r') as f:
            ans = f.read()

        print('{} {}'.format(inpf, ansf))
        print(score(inp, ans))
