from __future__ import division
import argparse
import numpy as np
from scipy import misc
import pylab
import matplotlib.pyplot as plt
import matplotlib.colors as color

parser = argparse.ArgumentParser()
parser.add_argument('-c')

args = parser.parse_args()
csvFile = open(args.c, 'r')
allLines = csvFile.readlines()
numLines = len(allLines)
header = allLines[0]

def groupByMovies():
    print "grouping movies..."
    movToUsers = {}
    for i in xrange(1, numLines):
        curLine = allLines[i]
        pid = curLine[0:9]
        uid = curLine[11:19]
        if uid == '05914897':
            # unknown user
            continue
        if pid not in movToUsers:
            movToUsers[pid] = [uid]
        else:
            if uid in movToUsers[pid]:
                #print "Duplicate pid-uid in csv?" 
                continue
            movToUsers[pid].append(uid)
    return movToUsers

def groupByUsers():
    print "grouping users..."
    userToMovies = {}
    for i in xrange(1, numLines):
        curLine = allLines[i]
        pid = curLine[0:9]
        uid = curLine[11:19]
        if uid == '05914897':
            # unknown user
            continue
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


    plt.hist(allAvgs, bins=20)
    plt.savefig('test_allAvgs_1000.png')

    print "Average avg:", avgAvg

if __name__ == '__main__':
    mtu = groupByMovies()
    print len(mtu)
    print "=============================="
    utm = groupByUsers()
    print len(utm)

    getPairDistances(mtu, utm)
    exit()
