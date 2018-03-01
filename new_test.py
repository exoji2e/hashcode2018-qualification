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

def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve(seed, inp, log):
    # TODO: Solve the problem
    random.seed(seed)
    ns = parse(inp)
    B, T, rides, C, R, N, F = ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F
    
    assert (B, T, rides, C, R, N, F) == (ns.B, ns.T, ns.rides, ns.C, ns.R, ns.N, ns.F)

    cars = [(0, 0, 0, i) for i in range(F)]

    orders = set(rides)

    car2 = [[] for _ in range(F)]

    no = 0
    X = sum(r.p_s[0] for r in orders)
    Y = sum(r.p_s[1] for r in orders)
    
    while cars:
        next_itr = []
        for c in cars:
            if len(orders) == 0:
                continue
            i = c[-1]
            log.debug(i)
            minsc = 0
            bestr = None
            sframme = None
            target = (random.randint(0, R-1), random.randint(0, C-1))
            xi = float(X)/len(orders)
            yi = float(Y)/len(orders)
            w = 1
            for r in orders:
                d = dist(r.p_s, (c[1],c[2]))
                
                framme = d + c[0]
                waste = d + max(0, r.t_s - framme)
                lastarr = r.t_f - dist(r.p_s, r.p_f)
                if framme > lastarr: continue

                pts = dist(r.p_s, r.p_f) + (B if framme <= r.t_s else 0)

                fac = random.random()*10

                # sc = float(pts)/(waste*fac+ dist(r.p_s, r.p_f))
                #sc = float(pts)/(dist((xi, yi), r.p_s)*(waste + 1)) if no > 0 else float(dist(target, r.p_s))/max(r.t_s - framme, 1)
                sc = float(pts)/((w*dist((xi, yi), r.p_s) + (2-w)*dist((xi, yi), r.p_f))*(waste + 1))
                if sc > minsc:
                    minsc = sc
                    bestr = r
                    sframme = framme
            if bestr:
                car2[i].append(bestr.i)
                orders.remove(bestr)
                c = (max(sframme, bestr.t_s) + dist(bestr.p_s, bestr.p_f), bestr.p_f[0], bestr.p_f[1], c[-1])
                next_itr.append(c)
                X -= bestr.p_s[0]
                Y -= bestr.p_s[1]
        no += 1
        cars = next_itr


            
            

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
        #show(out)

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

