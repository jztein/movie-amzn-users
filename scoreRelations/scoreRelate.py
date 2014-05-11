from __future__ import division
import argparse
import numpy as np
from scipy import misc
import pylab
import matplotlib.pyplot as plt
import matplotlib.colors as color
from time import time
import cPickle
from math import sqrt

parser = argparse.ArgumentParser()
parser.add_argument('-s', help="all scores txt")
parser.add_argument('--utm', help="utm = user: movies")
parser.add_argument('--mtu', help="mtu = movie: users")
parser.add_argument('--uts', help="uts = user: scores")
parser.add_argument('--stu', help="stu = score: users")
parser.add_argument('--stm', help="stm = score: moviess")
parser.add_argument('--mts', help="mts = movie: scores")
args = parser.parse_args()

globalAvg = None

# is this more performant than a C for-loop?
def getGlobalAverage():
    global globalAvg
    if not globalAvg:
        print "Getting global avg for the first time..."
        scoresFile = open(args.s, 'r')
        allScores = [float(s) for s in scoresFile.readlines()]
        globalAvg = sum(allScores) / len(allScores)
        print "==> global avg:", globalAvg
    else:
        return globalAvg

def getData():
    #utmF = open(args.utm, 'r')
    #mtuF = open(args.mtu, 'r')
    utsF = open(args.uts, 'rb')
    uts = cPickle.load(utsF)
    stu1to5 = [None, None, None, None, None]
    for i in xrange(1, 6):
        stu1to5[i-1] = open("%s%d.txt" % (args.stu, i), 'r').readlines()
    #stmF = open(args.stm, 'r')
    #mtsF = open(args.mts, 'r')

    print "UTS"
    print uts
    print "####################"
    print "STU"
    for stu in stu1to5:
        for u in stu:
            print u[:-1],
        print

    return {'uts':uts, 'stu':stu}

def avg(list):
    return sum(list) / len(list)

# stu=> score: users, uts=> user: scores
# TODO: plot histograms and stuff
def usersToScoresStuff(stu, uts):
    def getUserAverages():
        print "# get user averages"
        allAvgs = [avg(uts[user]) for user in uts]
        return allAvgs
    allAvgs = getUserAverages()
    print "ALL averages:", allAvgs

    # get user's average dist from their own average 
    def getUserAvgDistFromAvg():
        print "# get user average dist from their own average"
        allDists = [0.0 for x in xrange(len(uts))]
        i = 0
        for user in uts:
            scores = uts[user] 
            dists = [abs(s - allAvgs[i]) for s in scores]
            print "#:", dists
            allDists[i] = avg(dists)
            i += 1
        print allDists
        return allDists
    avgDist_u_ownAvg = getUserAvgDistFromAvg()

    # get user's average dist from global average
    def getUserAvgDistFromGlobalAvg():
        print "# User's average dist from global average"
        allDists = [0.0 for x in xrange(len(uts))]
        i = 0
        for user in uts:
            scores = uts[user] 
            dists = [abs(s - globalAvg) for s in scores]
            print "@:", dists
            allDists[i] = avg(dists)
            i += 1
        print allDists
        return allDists
    avgDist_u_gAvg = getUserAvgDistFromGlobalAvg()
    
    def distUserAvgGlobalAvg():
        print "# Dist between user avg and global avg"
        dists = [abs(avg - globalAvg) for avg in allAvgs]
        print dists
        return dists
    dist_uAvg_gAvg = distUserAvgGlobalAvg()

    # high = 5.0, # low = 1.0, # mid = 3.0
    def classifyHighLowMid():
        print "# Classify high low mid"
        highThreshold = (5.0 + globalAvg)/2
        lowThreshold = (1.0 + globalAvg)/2
        trueMid = (3.0 + globalAvg)/2
        print "ht:", highThreshold
        print "lt:", lowThreshold
        print "True middle:", trueMid

        i = 0
        users = uts.keys()
        high, mid, low = [], [], []
        for avg in allAvgs:
            user = users[i]
            print user, "=>", avg
            if highThreshold < avg and avg <= 5.0:
                high.append(user)
            elif lowThreshold < avg and avg <= highThreshold:
                mid.append(user)
            else:
                low.append(user)
            i += 1

        print "High:", high
        print "Mid:", mid
        print "Low:", low
        return high, mid, low

    classifyHighLowMid()

    # cluster?

    def med(dists):
        dists = sorted(dists)
        return dists[int(len(dists)/2)]

    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print ">> all averages\n", allAvgs, med(allAvgs), avg(allAvgs)
    x = avgDist_u_ownAvg
    print ">> avg dist of u from own avg", avgDist_u_ownAvg, med(x), avg(x)
    x = avgDist_u_gAvg
    print ">> avg dist of u from global avg", avgDist_u_gAvg, med(x), avg(x)
    x = dist_uAvg_gAvg
    print ">> dist of u's avg from global avg", dist_uAvg_gAvg, med(x), avg(x)

    # TODO: classify users according to distances
    def classifyByDist(dists):
        # dist can be any type
        # find 'median' or 'mean of lowest-highest'?
        median = dists[int(len(dists)/2)]
        mean = avg(dists)
        
        high, low = [], []
        # idea: if more than mean, high deviation. else, low.
        for d in dists:
            if d > mean:
                high.append(d)
            else:
                low.append(d)
        print "High:", high
        print "Low:", low
        return high, low

    classifyByDist(allAvgs)
    classifyByDist(avgDist_u_ownAvg)
    classifyByDist(avgDist_u_gAvg)
    classifyByDist(dist_uAvg_gAvg)

def playWithData():
    getGlobalAverage()
    data = getData()
    uts = data['uts']
    stu = data['stu']
    usersToScoresStuff(stu, uts)


if __name__ == '__main__':
    playWithData()
    exit(0)
