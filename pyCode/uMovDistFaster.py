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
parser.add_argument('--breakdown', action="store_true")

args = parser.parse_args()
csvFile = open(args.c, 'r')
allLinesCsv = csvFile.readlines()
numLines = len(allLinesCsv)
header = allLinesCsv[0]

avgFile = open('avgs.txt', 'w')

def distributionOfMoviesUsers(pids, uids):
    print "plotting..."

    plt.scatter(pids, uids, alpha=0.3)
    plt.savefig("scatterFastest.png")

def shortenFile():
    smallFile = open('aMsmall_Ascii.csv', 'w')
    smallFile.write(allLinesCsv[0])
    print "reducing lines..."

    for i in xrange(1, numLines, 1000):
        smallFile.write(allLinesCsv[i])

    smallFile.close()

def breakdownLines(allLines):
    pidArr = np.zeros(numLines-1)
    uidArr = np.zeros(numLines-1)

    for i in xrange(1, numLines):
        curLine = allLines[i].split(',')
        pid = curLine[0]
        uid = curLine[1]
        pidArr[i-1] = pid
        uidArr[i-1] = uid

    np.savez_compressed("pid.npz", pidArr)
    np.savez_compressed("uid.npz", uidArr)

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
    plt.savefig("fastestAllAvgs.png")

if __name__ == '__main__':
    startTime = time()

    if args.breakdown:
        print "breaking down and saving uid and pid to npz's..."
        breakdownLines(allLinesCsv)
        t = time() - startTime
        print "time to breakdown:", t

    print "reading npz files..."
    npzFile = np.load("uid.npz", mmap_mode=None)
    uids = npzFile[npzFile.files[0]]
    print "UID SHAPE:", uids.shape
    npzFile = np.load("pid.npz", mmap_mode=None)
    pids = npzFile[npzFile.files[0]]
    print "PID SHAPE:", pids.shape
    t = time() - startTime
    print "time to load uid and pid arrs:", t

    #distributionOfMoviesUsers(pids, uids)
    #t = time() - startTime
    #print ": time dist of movie users:", t
    #exit()

    mtu = groupByMovies(pids, uids)
    t = time() - startTime
    print len(mtu), ": time:", t
    print "=============================="
    utm = groupByUsers(pids, uids)
    t = time() - startTime
    print len(utm), ": time:", t

    getPairDistances(mtu, utm)
    t = time() - startTime
    print ": time:", t
    exit()
