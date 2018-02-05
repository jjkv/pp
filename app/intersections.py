# install this stuff before using module
from intervaltree import Interval, IntervalTree
from interval import interval
import functools
# interface for interval intersections

# quasi useful conversion functions between Interval and interval
def Itoi(x):
    return interval[x.begin, x.end]

def itoI(x):
    return Interval(x[0][0], x[0][1])

# IntervalTree to list of int tuples representing intervals
def tree_to_list(t):
    temp = []
    for i in sorted(t):
        temp.append((i[0], i[1]))
    return temp

# two ways to get an IntervalTree:

# takes list of tuples (a la tree_to_list())
def list_to_intervaltree(l):
    t = IntervalTree()
    for i in l:
        x = Interval(i[0], i[1])
        t.add(x)

    return t

# this one takes a list of intervals (hense itoI)
def intervals_to_tree(l):
    return IntervalTree(list(map(itoI, l)))

# the logic, this needs work:

# list of intervals representing the intersection of IntervalTrees t1 & t2
# O(|t1| * |t2|) worst case, is probably faster as many out of bounds intervals are ignored
def intervaltree_intersections(t1, t2):
    inter = []
    for i in t2:
        overlaps = t1[i.begin:i.end]
        ii = interval[i.begin, i.end]
        for o in overlaps:
            io = interval[o.begin, o.end]
            inter.append(io & ii)
    return inter

# absorbs redundant intervals
# ex. (1, 3), (1, 2) becomes (1, 3)
def condense_intervals(intervals):
    if not intervals:
        return intervals
    else:
        temp = functools.reduce(lambda x,y: x | y, intervals)
        return [x for x in temp.components]

# main, import this and all the work is done
# takes a list of tuple intervals and 
# ex. [(1, 3), (4,6)] & [(2, 3.5), (5, 8), (10, 1)] becomes
# [(2, 3), (5, 6)]
# tbh why isn't this built into IntervalTree...

# update: this function doesn't work at all, using the helper functions instead
def intersection_minutes(l1, l2):
    t1, t2 = list_to_intervaltree(l1), list_to_intervaltree(l2)
    intertree = intervaltree_intersections(t1, t2)
    interlist = condense_intervals(intertree)
    newtree = intervals_to_tree(interlist)
    return tree_to_list(newtree)

# takes the return of intersection minutes and computes the total amount of free time
def total_free_time(l):
    if l:
        return functools.reduce((lambda x,y: x + y), (list(map(lambda x: x[1] - x[0], l))))
    else:
        return 0

#x = list_to_intervaltree([(120, 180)])
#print(str(sorted(x)))
