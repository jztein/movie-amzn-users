'''
USAGE:
# prelimClusters()
$ python kmeansPP.py --utm /Users/kristen/Documents/1UCLA/CS199/pyCode/utm.pkl --mtu /Users/kristen/Documents/1UCLA/CS199/pyCode/mtu.pkl -g groupedC.pkl -k hashedC.pkl --prelim
MTU.LEN 207533
UTM.LEN 1224266
num clusters: 28019
time taken: 395.305128813

# classifyPrelimClusters()
$ python kmeansPP.py -k hashedC.pkl --finePrelim --mts /Users/kristen/Documents/1UCLA/CS199/pyCode/mts.pkl -f fineC.pkl
time taken: 6.35967183113

# kmeans++
$ python kmeansPP.py --mts /Users/kristen/Documents/1UCLA/CS199/pyCode/mts.pkl -c fineC.pkl -f featC.pkl --kmeansPP --getFeats
$ python kmeansPP.py --mts /Users/kristen/Documents/1UCLA/CS199/pyCode/mts.pkl -c fineC.pkl -f featC.pkl --kmeansPP
num classified prelim clusters: 34730 (reduced 207533 movies by ~6 times)
num feats: 34730
time taken: 0.610143899918

# Kmeans++ from saved centroids
$ python kmeansPP.py -f featC.pkl --kmeansPPsaved -s featKmeansPP_clusters.pkl
time taken: 58.4788708687
$ ls -l | grep KmeansPP_
-rw-r--r--  1 kristen  staff   266763 Jun  4 12:17 featKmeansPP_clusters.pkl

'''
from __future__ import division
import argparse
import numpy as np
from scipy import stats
import cPickle
from time import time
import random

rand = random.random
rr = random.randrange
dist = np.linalg.norm

GLOBAL_AVG_SCORE = 4.12

parser = argparse.ArgumentParser()
parser.add_argument('-g', help='movies labeled with hash')
parser.add_argument('-k', help='hashed pkl')
parser.add_argument('-c', help='classified prelim pkl to finely hashed pkl')
parser.add_argument('-f', help='features hash pkl')
parser.add_argument('-s', help='save kmeans clusters in pkl')
parser.add_argument('--mtu')
parser.add_argument('--utm')
parser.add_argument('--mts')

parser.add_argument('--prelim', help='get prelim clusters', 
                    action='store_true')
parser.add_argument('--finePrelim', help='classify prelim clusters', 
                    action='store_true')
parser.add_argument('--kmeansPP', help='do kmeans++ clustering',
                    action='store_true')
parser.add_argument('--getFeats', help='getFeatures() from scratch',
                    action='store_true')
parser.add_argument('--kmeansPPsaved', 
                    help='kmeans++ but already have centroids', 
                    action='store_true')

args = parser.parse_args()

def prelimClusters():
    f = open(args.mtu, 'rb')
    mtu = cPickle.load(f)
    f.close()

    f = open(args.utm, 'rb')
    utm = cPickle.load(f)
    f.close()

    print "MTU.LEN %d" % len(mtu)
    print "UTM.LEN %d" % len(utm)

    preClusters = {}
    hashClusters = {}
    hashVal = -1
    for movie in mtu:
        if not movie in preClusters:
            hashVal += 1
            preClusters[movie] = hashVal
            hashClusters[hashVal] = [movie]
            
        nUsers = mtu[movie]
        for neighbor in nUsers:
            nMovies = utm[neighbor]
            for neighborMovie in nMovies:
                if not neighborMovie in preClusters:
                    preClusters[neighborMovie] = hashVal
                    hashClusters[hashVal].append(neighborMovie)

    print "num clusters:", hashVal - 1
    f = open(args.k, 'wb')
    cPickle.dump(hashClusters, f)
    f.close()
    f = open(args.g, 'wb')
    cPickle.dump(preClusters, f)
    f.close()

def classifyPrelimClusters():
    f = open(args.k, 'rb')
    hashClusters = cPickle.load(f)
    f.close()

    f = open(args.mts, 'rb')
    mts = cPickle.load(f)
    f.close()

    newHashVal = len(hashClusters)

    finerHashClusters = {}

    # divide each prelim cluster into more liked/ disliked
    for hash in hashClusters:
        movieCluster = hashClusters[hash]
        goodCluster = []
        badCluster = []
        for movie in movieCluster:
            scores = np.array(mts[movie])
            avgScore = np.mean(scores)
            if avgScore > GLOBAL_AVG_SCORE:
                goodCluster.append(movie)
            else:
                badCluster.append(movie)
        if not goodCluster:
            finerHashClusters[hash] = badCluster
        elif not badCluster:
            finerHashClusters[hash] = goodCluster
        else:
            finerHashClusters[hash] = goodCluster
            finerHashClusters[newHashVal] = badCluster
            newHashVal += 1

    f = open(args.c, 'wb')
    cPickle.dump(finerHashClusters, f)
    f.close()

def getFeatures(groups):
    f = open(args.mts, 'rb')
    mts = cPickle.load(f)
    f.close()

    featureGroups = {}
    for hash in groups:
        group = groups[hash]
        # get feats
        # look at all the movies
        groupStats = []
        for movie in group:
            scores = np.array(mts[movie])
            scoreStats = np.array((np.mean(scores), np.nanstd(scores), 
                                   len(scores)))
            groupStats.append(scoreStats)
        sumGStats = sum(groupStats)
        numStats = len(groupStats)
        meanStats = np.zeros(3)
        meanStats[0] = sumGStats[0] / numStats
        meanStats[1] = sumGStats[1] / numStats
        meanStats[2] = sumGStats[2] / numStats
        featureGroups[hash] = meanStats

    f = open(args.f, 'wb')
    cPickle.dump(featureGroups, f)
    f.close()

    return featureGroups

def calcProb(feat, centroid, sum2):
    Dx = dist(feat - centroid)**2
    return Dx / sum2

# 2007 k-means++: The Advantages of Careful Seeding, Arthur & Vassilvitskii
# http://ilpubs.stanford.edu:8090/778/1/2006-13.pdf
def kmeansPP(k=5):
    f = open(args.c, 'rb')
    fineHashClusters = cPickle.load(f)
    f.close()

    print "num classified prelim clusters:", len(fineHashClusters)

    if args.getFeats:
        features = getFeatures(fineHashClusters)
    else:
        f = open(args.f, 'rb')
        features = cPickle.load(f)
        f.close()

    numFeats = len(features)
    print "num feats:", numFeats

    # get ranges
    dim2 = [0 for x in xrange(numFeats)]
    dim1 = [0 for x in xrange(numFeats)] 
    dim0 = [0 for x in xrange(numFeats)]
    for i in xrange(numFeats):
        dim0[i] = features[i][0]
        dim1[i] = features[i][1]
        dim2[i] = features[i][2]
    min0, max0 = min(dim0), max(dim0)
    min1, max1 = min(dim1), max(dim1)
    min2, max2 = min(dim2), max(dim2)
    
    # Start kmeans++ for real
    # 1a. pick random first centroid
    randFirstCentroid = np.array([rr(min0, max0), 
                                  rr(min1, max1), 
                                  rr(min2, max2)])

    sum2 = dist(sum((features.values() - randFirstCentroid)**2))
    nextCentroid = np.array([None, None, None])
    # 1b. pick next centroid
    for hash in features:
        feat = features[hash]
        bbq = calcProb(feat, randFirstCentroid, sum2)
        if rand() < bbq:
            nextCentroid = feat
            print "picked 1b centroid"
            break

    centroids = [randFirstCentroid, nextCentroid]
    sum2s = [dist(sum((features.values()-c)**2)) for c in centroids]
    # 1c. pick up to k centroids
    while len(centroids) < k:
        for hash in features:
            feat = features[hash]
            minDist = dist(feat - centroids[0])
            minIdx = 0
            for i in xrange(1, len(centroids)):
                c = centroids[i]
                curDist = dist(feat - c)
                if curDist < minDist:
                    minDist = dist
                    minIdx = i
            sum2 = sum2s[minIdx]
            c = centroids[minIdx]
            prob = calcProb(feat, c, sum2)
            if rand() < prob:
                centroids.append(feat)
                sum2s.append(dist(sum((features.values()-feat)**2)))

    print "all k=%d centroids" % k
    print centroids

    f = open("centroids_SAVED.pkl", 'wb')
    cPickle.dump(centroids, f)
    f.close()

    # 2. do standard kmeans
    kmeans(centroids, features)

def kmeansPP_withSavedCentroids():
    f = open("centroids_SAVED.pkl", 'rb')
    centroids = cPickle.load(f)
    f.close()

    f = open(args.f, 'rb')
    features = cPickle.load(f)
    f.close()

    kmeans(centroids, features)

def kmeans(centroids, data):
    k = len(centroids)

    oldClusters = {}
    # repeat until clusters no longer change
    while True:
        clusters = {}
        minIdx = 0
        for i in xrange(k):
            clusters[i] = []
        for feat in data:
            minDx, minIdx = dist(feat - centroids[0]), 0
            for i in xrange(1, k):
                c = centroids[i]
                curDist = dist(feat - c)
                if minDx > curDist: 
                    minDx = curDist
                    minIdx = i
            clusters[minIdx].append(feat)
        if oldClusters == clusters:
            break
        else:
            oldClusters = clusters
            # calculate new centroids
            newCentroids = centroids[:]
            for i in clusters:
                cluster = clusters[i]
                if cluster:
                    newCentroids[i] = (sum(cluster) / len(cluster))
            centroids = newCentroids

    f = open(args.s, 'wb')
    cPickle.dump(oldClusters, f)
    f.close()

def main():
    t = time()
    if args.prelim:
        prelimClusters()
    if args.finePrelim:
        classifyPrelimClusters()
    if args.kmeansPP:
        kmeansPP()
    elif args.kmeansPPsaved:
        kmeansPP_withSavedCentroids()
    print "time taken:", time() - t
    pass

if __name__ == '__main__':
    main()
    exit()
