#!/usr/bin/env pypy
import argparse
import random
import glob
from collections import namedtuple
from sortedcontainers import SortedList

Ride = namedtuple('Ride', ['i', 'p_s', 'p_f', 't_s', 't_f'])
Coord = namedtuple('Point', ['x', 'y'])
CarState = namedtuple('CarState', ['t', 'p_s', 'p_f', 'win', 'i', 'order'])


class Point(Coord):
    def dist(self, other):
        return sum((abs(self.x - other.x), abs(self.y - other.y)))


def parse(inp):
    itr = (map(int, li.split()) for li in inp.split('\n') if li)
    R, C, F, N, B, T = next(itr)
    rides = [Ride(i, Point(a, b), Point(x, y), s, f) for i, (a, b, x, y, s, f) in enumerate(itr)]

    return argparse.Namespace(B=B, T=T, rides=rides, C=C, R=R, N=N, F=F)


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def solve(seed, inp, log):
    random.seed(seed)
    ns = parse(inp)
    B, T, rides, C, R, N, F = ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F

    orders = set(rides)

    X = sum(r.p_s[0] for r in orders)
    Y = sum(r.p_s[1] for r in orders)

    CarStates = [[CarState(0, Point(0, 0), Point(0, 0), 0, i, -1)] for i in range(F)]
    cars = SortedList([CarStates[i][0] for i in range(F)])
    pw = 1 + 4*random.random()
    pp = 0.5 + 0.5*random.random()
    wf = 1 + 5*random.random()
    bw = 2*random.random()

    log.critical('seed:{}\tpw:{}\tpp:{}'.format(seed, pw, pp))
    log.critical('wf:{}\tbw:{}'.format(wf, bw))
    while cars:
        c = cars.pop(0)
        if len(orders) == 0:
            continue
        minsc = 0
        bestr = None
        best_state = None

        xi = float(X)/len(orders)
        yi = float(Y)/len(orders)
        med = (xi, yi)
        for r in orders:
            d = dist(r.p_s, c.p_f)

            framme = d + c[0]
            waste = d + max(0, r.t_s - framme)
            lastarr = r.t_f - dist(r.p_s, r.p_f)
            if framme > lastarr: continue

            pts_real = dist(r.p_s, r.p_f) + (B if framme <= r.t_s else 0)
            pts = dist(r.p_s, r.p_f) + (bw*B if framme <= r.t_s else 0)

            def w(p, ds, df, waste):
                return float(p)**pp/((ds + wf*df)*(waste**pw + 1))

            sc = w(pts, dist(med, r.p_s), dist(med, r.p_f), waste)
            if sc > minsc:
                minsc = sc
                bestr = r
                best_state = CarState(max(framme, r.t_s) + dist(r.p_s, r.p_f),
                                      r.p_s, r.p_f, c.win + pts_real, c.i, r.i)
        if bestr:
            orders.remove(bestr)
            cars.add(best_state)
            CarStates[c.i].append(best_state)
            X -= bestr.p_s[0]
            Y -= bestr.p_s[1]

    ch = True
    while ch:
        ch = False
        for i, states in enumerate(CarStates):
            maxsc = states[-1].win
            cs = None
            for r in orders:
                lastarrive = r.t_f - dist(r.p_s, r.p_f)
                n = len(states) - 1
                while n >= 0 and states[n].t + dist(states[n].p_f, r.p_s) > lastarrive:
                    n -= 1
                if n < 0: continue
                arrive = states[n].t + dist(states[n].p_f, r.p_s)
                sc = dist(r.p_s, r.p_f) + (B if arrive <= r.t_s else 0) + states[n].win
                if sc > maxsc:
                    cs = CarState(max(arrive, r.t_s) + dist(r.p_s, r.p_f), r.p_s, r.p_f, sc, states[n].i, r.i)
                    keep = n+1
                    maxsc = sc
            if cs:
                ch = True
                replc = rides[cs.order]
                log.debug('Updating score: {} {}'.format(states[-1].win, maxsc))
                for s in states[keep:]:
                    ride = rides[s.order]
                    orders.add(ride)
                orders.remove(replc)
                CarStates[i] = states[:keep] + [cs]

    out = []

    for v in CarStates:
        v = v[1:]
        s = str(len(v)) + ' '
        s += ' '.join(map(lambda x: str(x.order), v))
        out.append(s)

    assert (B, T, rides, C, R, N, F) == (ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F)

    return '\n'.join(out)


def show(out):
    # TODO: Print the solution here
    print(out)


def score(inp, out):
    ns = parse(inp)
    B, T, rides, C, R, N, F = ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F

    bonus_miss, dist_miss = 0, 0
    ride_waste = 0
    tot_dist = 0

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
        for i, r in ((i, rides[i]) for i in ride_ids):
            assert i in ride_set
            ride_set -= {i}
            start = max(time + r.p_s.dist(cur_p), r.t_s)
            ride_waste += r.p_s.dist(cur_p) + start - r.t_s
            if start == r.t_s:
                score += B
            else:
                bonus_miss += 1
            dist = r.p_s.dist(r.p_f)
            if start + dist > r.t_f:
                print('{} {} {}'.format(start, dist, r.t_f))
            assert start + dist <= r.t_f
            cur_p = r.p_f
            tot_dist += dist
            score += dist
            time = start + dist

    assert (B, T, rides, C, R, N, F) == (ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F)

    if __name__ == '__main__' and args.s:
        bonus_miss_score = bonus_miss * B
        for i in ride_set:
            dist_miss += rides[i].p_s.dist(rides[i].p_f)

        print("F: {}, N: {}, B: {}".format(F, N, B))
        print("bonus_miss_ratio: {:.0f}%, bonus_miss_score: {}, ride_miss: {}, dist_miss: {}".format(100*float(bonus_miss)/N, bonus_miss_score, len(ride_set), dist_miss))
        print("ride_waste: {} ({:.0f}%)".format(ride_waste, (ride_waste * 100.) / (ride_waste + tot_dist)))
        # show(out)

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

