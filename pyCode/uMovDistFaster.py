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
    newAllLines = []
    for i in xrange(1, numLines):
        curLine = allLines[i]
        newAllLines.append(curLine.split(','))
    return newAllLines

def groupByMovies(allLines):
    print "grouping movies..."
    movToUsers = {}
    for i in xrange(numLines-1):
        curLine = allLines[i]
        pid = curLine[0]
        uid = curLine[1]
        if pid not in movToUsers:
            movToUsers[pid] = [uid]
        else:
            if uid in movToUsers[pid]:
                #print "Duplicate pid-uid in csv?" 
                continue
            movToUsers[pid].append(uid)

    return movToUsers

def groupByUsers(allLines):
    print "grouping users..."
    userToMovies = {}
    for i in xrange(numLines-1):
        curLine = allLines[i]
        pid = curLine[0]
        uid = curLine[1]
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
    plt.savefig("faster1000Avgs.png")

if __name__ == '__main__':
    startTime = time()

    newAllLines = breakdownLines(allLinesCsv)
    print len(newAllLines), ": time:", time() - startTime

    mtu = groupByMovies(newAllLines)
    print len(mtu), ": time:", time() - startTime
    print "=============================="
    utm = groupByUsers(newAllLines)
    print len(utm), ": time:", time() - startTime

    getPairDistances(mtu, utm)
    print ": time:", time() - startTime
    exit()
