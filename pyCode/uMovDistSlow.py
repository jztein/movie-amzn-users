from __future__ import division
import argparse
import numpy as np
from scipy import misc
import pylab
import matplotlib.pyplot as plt
import matplotlib.colors as color
from time import time

parser = argparse.ArgumentParser()
parser.add_argument('-c')
parser.add_argument('-p')
parser.add_argument('-u')

args = parser.parse_args()
csvFile = open(args.c, 'r')
allLinesCsv = csvFile.readlines()
numLines = len(allLinesCsv)
header = allLinesCsv[0]

avgFile = open('avgs.txt', 'w')

def shortenFile():
    smallFile = open('aMsmall_Ascii.csv', 'w')
    smallFile.write(allLinesCsv[0])
    print "reducing lines..."

    for i in xrange(1, numLines, 1000):
        smallFile.write(allLinesCsv[i])

    smallFile.close()

def breakdownLines(allLines):
    pids = [0 for x in xrange (numLines-1)]
    uids = [0 for x in xrange (numLines-1)]

    pf = open(args.p, 'w')
    uf = open(args.u, 'w')

    for i in xrange(1, numLines):
        curLine = allLines[i].split(',')
        pids[i-1] = curLine[0]
        uids[i-1] = curLine[1]
        pf.write("%s\n" % pids[i-1])
        uf.write("%s\n" % uids[i-1])

    pf.close()
    uf.close()

    return pids, uids

def getSavedPidsUids():
    pf = open(args.p, 'r')
    uf = open(args.u, 'r')
    pids = pf.readlines()
    uids = uf.readlines()
    pf.close()
    uf.close()

    return pids, uids

def groupAbyBs(pids, uids):
    print "grouping..."
    movToUsers = {}
    for i in xrange(numLines):
        pid = pids[i]
        uid = uids[i]
        if pid not in movToUsers:
            movToUsers[pid] = [uid]
        else:
            if uid in movToUsers[pid]:
                #print "Duplicate pid-uid in csv?" 
                continue
            movToUsers[pid].append(uid)

    return movToUsers


def groupByMovies(pids, uids):
    print "grouping movies..."
    movToUsers = {}
    for i in xrange(numLines-1):
        pid = pids[i]
        uid = uids[i]
        if pid not in movToUsers:
            movToUsers[pid] = [uid]
        else:
            if uid in movToUsers[pid]:
                #print "Duplicate pid-uid in csv?" 
                continue
            movToUsers[pid].append(uid)

    return movToUsers

def groupByUsers(pids, uids):
    print "grouping users..."
    userToMovies = {}
    for i in xrange(numLines-1):
        pid = pids[i]
        uid = uids[i]
        if uid not in userToMovies:
            userToMovies[uid] = [pid]
        else:
            if pid in userToMovies[uid]:
                #print "Duplicate uid-pid in csv?" 
                continue
            userToMovies[uid].append(pid)

    return userToMovies

def getPairDistances(movToUsers, userToMovs):
    allAvgs = []
    for uid in userToMovs:
        userAvg = 0
        userMovs = userToMovs[uid]
        for pid in userMovs:
            mappedUids = movToUsers[pid]
            userAvg += len(mappedUids)
        userAvg /= len(userMovs)
        allAvgs.append(userAvg)
    sumAvgs = sum(allAvgs)
    avgAvg = sumAvgs / len(allAvgs)
    print "Average avg:", avgAvg

    for avg in allAvgs:
        avgFile.write("%f\n" % avg)
    avgFile.write("Average avg: %f" % avgAvg)
    avgFile.close()

    plt.hist(allAvgs, bins=20)
    plt.savefig("slowAllAvgs.png")

def distributionOfMoviesUsers(pids, uids):
    print "plotting..."

    plt.scatter(pids, uids, alpha=0.3)
    plt.show()

if __name__ == '__main__':
    startTime = time()

    pids, uids = breakdownLines(allLinesCsv)
    exit()

    pids, uids = getSavedPidsUids()
    print len(pids), ": time:", time() - startTime

    '''
    distributionOfMoviesUsers(pids, uids)
    print "distr of movies-users time:", time() - startTime
    exit()
    '''

    mtu = groupByMovies(pids, uids)
    print len(mtu), ": time:", time() - startTime
    print "=============================="
    utm = groupByUsers(pids, uids)
    print len(utm), ": time:", time() - startTime

    getPairDistances(mtu, utm)
    print ": time:", time() - startTime
    exit()
