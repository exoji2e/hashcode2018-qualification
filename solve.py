#!/usr/bin/env pypy
import argparse
import random
import glob
from collections import namedtuple

Ride = namedtuple('Ride', ['i', 'p_s', 'p_f', 't_s', 't_f'])
Coord = namedtuple('Point', ['x', 'y'])


class Point(Coord):
    def dist(self, other):
        return sum((abs(self.x - other.x), abs(self.y - other.y)))


def parse(inp):
    itr = (map(int, li.split()) for li in inp.split('\n') if li)
    R, C, F, N, B, T = next(itr)
    rides = [Ride(i, Point(a, b), Point(x, y), s, f) for i, (a, b, x, y, s, f) in enumerate(itr)]

    return argparse.Namespace(B=B, T=T, rides=rides, C=C, R=R, N=N, F=F)


def solve(seed, inp, log):
    # TODO: Solve the problem
    random.seed(seed)
    ns = parse(inp)
    B, T, rides, C, R, N, F = ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    assert (B, T, rides, C, R, N, F) == (ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F)

    cars = [(0, 0, 0)]*F

    orders = sorted(rides, key=lambda r:r.t_f - dist(r.p_s, r.p_f))

    car2 = [[] for _ in range(F)]


    for r in orders:
        best = -1
        v = 10000000000
        bestc = -1
        need2start = r.t_f - dist(r.p_s, r.p_f)
        for i, c in enumerate(cars):
            d = dist((c[1], c[2]), r.p_s)
            if d + c[0] <= need2start:
                if d + c[0] < v:
                    v = d+c[0]
                    best = i
                    bestc = c
        if best != -1:
            t_f = max(d + bestc[0], r.t_s) + dist(r.p_s, r.p_f)
            if t_f <= T:
                car2[best].append(r.i)
                cars[best] = (t_f, r.p_f[0], r.p_f[1])

    out = []
    for v in car2:
        s = str(len(v)) + ' '
        s += ' '.join(map(str, v))
        out.append(s)
    return '\n'.join(out)


def show(out):
    # TODO: Print the solution here
    print(out)

def score(inp, out):
    ns = parse(inp)
    B, T, rides, C, R, N, F = ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F

    bonus_miss, ride_miss, dist_miss = 0, 0, 0
    ride_waste = 0
    tot_dist = 0

    paths = []

    itr = (map(int, li.split()) for li in out.split('\n'))
    score = 0
    ride_set = set(range(N))
    for i in range(F):
        li = next(itr)
        M = li[0]
        ride_ids = li[1:]
        assert len(ride_ids) == M
        cur_p = Point(0, 0)
        time = 0
        path = [cur_p]
        for i, r in ((i, rides[i]) for i in ride_ids):
            assert i in ride_set
            path.append(r.p_s)
            ride_set -= {i}
            start = max(time + r.p_s.dist(cur_p), r.t_s)
            ride_waste += r.p_s.dist(cur_p) + start - r.t_s
            if start == r.t_s:
                score += B
            else:
                bonus_miss += 1
            dist = r.p_s.dist(r.p_f)
            assert start + dist <= r.t_f
            cur_p = r.p_f
            tot_dist += dist
            score += dist
            time = start + dist
            path.append(cur_p)
        paths.append(path)

    assert (B, T, rides, C, R, N, F) == (ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F)

    if __name__ == '__main__' and args.s:
        bonus_miss_score = bonus_miss * B
        for i in ride_set:
            dist_miss += rides[i].p_s.dist(rides[i].p_f)

        print("F: {}, N: {}, B: {}".format(F, N, B))
        print("bonus_miss_ratio: {:.0f}%, bonus_miss_score: {}, ride_miss: {}, dist_miss: {}".format(100*float(bonus_miss)/N, bonus_miss_score, len(ride_set), dist_miss))
        print("ride_waste: {} ({:.0f}%)".format(ride_waste, (ride_waste * 100.) / (ride_waste + tot_dist)))
        #show(out)

    if __name__ == "__main__" and args.s:
        from matplotlib.figure import Figure
        from matplotlib.axes import Axes
        from matplotlib.lines import Line2D
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        import numpy as np

        def norm_pair(p):
            return (float(p[0]) / R, float(p[1]) / C)

        fig = Figure(figsize=[16 * 4, 16 * 4])
        ax = Axes(fig, [.1, .1, .8, .8])
        fig.add_axes(ax)
        for path in paths:
            for i, (prev, nxt) in enumerate(zip(path[0:], path[1:])):
                prev_norm, nxt_norm = norm_pair(prev), norm_pair(nxt)
                line = Line2D((prev_norm[0], nxt_norm[0]), (prev_norm[1], nxt_norm[1]),
                              color='blue' if i % 2 else 'yellow')
                #ax.add_line(line)

        for ride in (rides[i] for i in ride_set):
            prev_norm, nxt_norm = norm_pair(ride.p_s), norm_pair(ride.p_f)
            t = float(ride.t_s) / T
            print(t, ride.t_s, T)
            line = Line2D((prev_norm[0], nxt_norm[0]), (prev_norm[1], nxt_norm[1]),
                          color=np.array([0, 1, 1]) + np.array([1, 0, 0])*t)
            ax.add_line(line)

        canvas = FigureCanvasAgg(fig)
        canvas.print_figure("line_ex.png")


    return score


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
