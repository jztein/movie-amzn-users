from __future__ import division # for float divide
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
allLines = csvFile.readlines()
numLines = len(allLines)

def distributionOfMoviesUsers():
    header = allLines[0]
    #pids = np.zeros(numLines-1)
    #uids = np.zeros(numLines-1)
    pids = [0 for i in xrange(numLines-1)]
    uids = [0 for i in xrange(numLines-1)]
    for i in xrange(1, numLines):
        curLine = allLines[i]
        pids[i-1] = curLine[0:9]
        uids[i-1] = curLine[11:19]

    print "plotting..."

    plt.scatter(pids, uids, alpha=0.3)
    plt.show()

def shortenFile():
    smallFile = open('aMsmall.csv', 'w')
    smallFile.write(allLines[0])
    print "reducing lines..."

    for i in xrange(1, numLines, 1000):
        smallFile.write(allLines[i])

    smallFile.close()

def groupMoviesByUser():
    userToMovies = {}
    startTime = time()
    print "grouping movies by user"
    for i in xrange(1, numLines):    
        uid = allLines[i][11:19]
        pid = allLines[i][0:9]
        # unknown user id
        if uid == '05914897':
            continue
        if uid not in userToMovies:
            userToMovies[uid] = [ pid ]
        else:
            if pid in userToMovies[uid]:
                print "THERE's duplicate entries in csv??", uid, pid
            userToMovies[uid].append(pid)
    print "finished grouping movies by user", time() - startTime
    return userToMovies

def getDistances(byPairs=False):
    userToMovies = groupMoviesByUser()
    startTime = time()
    sumAvgs = 0
    allAvgs = [0 for x in xrange(numLines-1)]
    i = 0
    for uid in userToMovies:
        curMovies = userToMovies[uid]
        #print uid, curMovies
        sum = 0
        for otherUid in userToMovies:
            if uid == otherUid:
                continue
            curOtherMovies = userToMovies[otherUid]
            count = 0
            for mov in curMovies:
                if mov in curOtherMovies:
                    count += 1
            sum += count
        if byPairs:
            avg = sum / (numLines - 2)
        else:
            avg = sum
        #print "#################################", avg
        allAvgs[i] = avg
        i += 1
        sumAvgs += avg
    avgAvg = sumAvgs / (numLines - 1)
    print "Average average:", avgAvg
    print "time to get avg:", time() - startTime
    print "Making hist..."
    plt.hist(allAvgs, bins=20)
    plt.savefig('allAvgs_small.png')
    print "Total time taken:", time() - startTime

if __name__ == '__main__':
    getDistances(byPairs=True)
    exit()
