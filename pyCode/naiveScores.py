from __future__ import division
import argparse
import numpy as np
from scipy import misc
import pylab
import matplotlib.pyplot as plt
import matplotlib.colors as color
from time import time
import uMovDistSlow
import cPickle

parser = argparse.ArgumentParser()
# csv file
parser.add_argument('-c') # all csv or scores file
parser.add_argument('-p') # pids file
parser.add_argument('-u') # uids file
parser.add_argument('--makescores', action='store_true')

args = parser.parse_args()
csvFile = open(args.c, 'r')
allLines = csvFile.readlines()
numLines = len(allLines)
header = allLines[0]

def setup():
    if args.makescores:
        print "Saving scores..."

        scoresFile = open("scores.txt", 'w')
        
        for i in xrange(1, numLines):
            values = allLines[i].split(',')
            scoresFile.write("%s\n" % values[4])

        scoresFile.close()
        exit(0)

    scores = [0.0 for x in xrange (numLines)]
    uids = [0 for x in xrange (numLines)]
    pids = [0 for x in xrange (numLines)]

    uidLines = open(args.u, 'r').readlines()
    pidLines = open(args.p, 'r').readlines()
    for i in xrange(numLines):
        uids[i] = int(uidLines[i])
        pids[i] = int(pidLines[i])
        scores[i] = float(allLines[i])

    return pids, uids, scores

def groupAbyScores(aids, scores, prefix):
    s1 = open("%s_scores_1.txt" % prefix, 'w')
    s2 = open("%s_scores_2.txt" % prefix, 'w')
    s3 = open("%s_scores_3.txt" % prefix, 'w')
    s4 = open("%s_scores_4.txt" % prefix, 'w')
    s5 = open("%s_scores_5.txt" % prefix, 'w')
    for i in xrange(numLines):
        s = scores[i]
        if s == 1.0:
            s1.write("%f\n" % s)
        elif s == 2.0:
            s2.write("%f\n" % s)
        elif s == 3.0:
            s3.write("%f\n" % s)
        elif s == 4.0:
            s4.write("%f\n" % s)
        elif s == 5.0:
            s5.write("%f\n" % s)
    s1.close()
    s2.close()
    s3.close()
    s4.close()
    s5.close()

def makeGroups(pids, uids, scores):
    t = time()
    # movies : users...
    print "movies: users..."
    mtu = uMovDistSlow.groupAbyBs(pids, uids)
    t = time() - t
    print 'group time:', t
    outfile = open('mtu.pkl', 'wb')
    cPickle.dump(mtu, outfile)
    outfile.close()
    t = time() - t
    print 'pickle time:',  t

    # users : movies...
    print "users: movies..."
    utm = uMovDistSlow.groupAbyBs(uids, pids)
    t = time() - t
    print t
    print 'group time:', t
    outfile = open('utm.pkl', 'wb')
    cPickle.dump(utm, outfile)
    outfile.close()
    t = time() - t
    print 'pickle time:',  t

    # scores : users...
    print "scores: users..."
    stu = groupAbyScores(uids, scores, 'uid')
    t = time() - t
    print t
    print 'group time:', t

    # users : scores...
    print "users: scores"
    uts = uMovDistSlow.groupAbyBs(uids, scores)
    t = time() - t
    print t
    print 'group time:', t
    outfile = open('uts.pkl', 'wb')
    cPickle.dump(uts, outfile)
    outfile.close()
    t = time() - t
    print 'pickle time:',  t

    # scores : movies...
    print "scores: movies..."
    stm = groupAbyScores(pids, scores, 'pid')
    t = time() - t
    print t
    print 'group time:', t

    # movies : scores...
    print "movies: scores..."
    mts = uMovDistSlow.groupAbyBs(pids, scores)
    t = time() - t
    print 'group time:', t
    outfile = open('mts.pkl', 'wb')
    cPickle.dump(mts, outfile)
    outfile.close()
    t = time() - t
    print 'pickle time:',  t

    return mtu, utm, uts, stu, mts, stm

if __name__ == '__main__':
    t = time()
    pids, uids, scores = setup()
    t = time() - t
    print 't:', t
    _, _, _, _, _, mts = makeGroups(pids, uids, scores)
    t = time() - t
    print 't:', t

    count = 0
    for key in mts:
        print key, mts[key]
        count += 1
        if count > 11:
            break

    exit(0)
