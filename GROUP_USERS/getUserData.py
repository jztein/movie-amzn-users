'''
User data by score features, text reviews, and kinds of movies rated.
- And helpfulness?

USAGE:

$ python getUserData.py --utf ../scoreRelations/utf.pkl --subjectivity ../textSubjectivity/subjResults_ALL_L.pkl --movieslabeled ../MovieRelations/pidToKmeans.pkl --utm ../pyCode/utm.pkl --uth ../pyCode/uth.pkl --output userData_ALL.pkl
GHOSTS: 0
num unknown users: 0
num users with data logged: 1224266
TIME: 11533.430819

42.8 MB output
'''
import argparse
import numpy as np
import cPickle
from time import time

NUM_DIMS = 20

parser = argparse.ArgumentParser()

parser.add_argument('--getuserdata', help='make userData_ALL.pkl')
# scoreRelations/utf.pkl
parser.add_argument('--utf',help='user to score-feats')
# textSubjectivity/uToSubj_ascii.pkl
parser.add_argument('--subjectivity') # file with subjectivity by user info
# MovieRelations/pidToKmeans.pkl
parser.add_argument('--movieslabeled') # file with movie clusters
# pyCode/utm.pkl
parser.add_argument('--utm', help='user to movies')
# pyCode/uth.pkl
parser.add_argument('--uth', help='user to helpfulness features')

parser.add_argument('--kdtree', help='build kdtree and analysis')
# userData_ALL.pkl
parser.add_argument('--data', help='user data made from getUserData')

# getuserdata: userData_ALL.pkl
# kdtree: kdtree_ALL.pkl
parser.add_argument('--output')

parser.add_argument('--subset', action='store_true')

parser.add_argument('--lsh', action='store_true')
parser.add_argument('--hashdata')
parser.add_argument('--datavec')
parser.add_argument('--haveDataVecs', action='store_true')

parser.add_argument('--normalize', action='store_true')

args = parser.parse_args()

def transANtoASCII(id):
    return ''.join([str(ord(x)) for x in id])

UNKNOWN_ASCII = transANtoASCII('unknown')

def getUserScoreFeats():
    f = open(args.utf,'rb')
    utf = cPickle.load(f)
    f.close()

    f = open(args.subjectivity, 'rb')
    utSubj = cPickle.load(f)
    f.close()

    f = open(args.movieslabeled, 'rb')
    mtLabel = cPickle.load(f)
    f.close()

    f = open(args.utm, 'rb')
    utm = cPickle.load(f)
    f.close()

    f = open(args.uth, 'rb')
    uth = cPickle.load(f)
    f.close()

    numUnknowns = 0
    ghosts = []

    # including 'unknown'-uid users, who we'll ignore
    numRawUsers = len(utf)

    userData = {}

    for user in utf:
        if user == UNKNOWN_ASCII:
            numUnknowns += 1
            continue

        # feat = (mean, std, num scorings)
        feat = utf[user]
        # help = (helpfulnessRatio, num helpfulness ratings)
        help = uth[user]
        # subjs = ratio of subjective comments
        subjs = utSubj[user]
        labelNums = [0 for x in range(10)]
        # user = [pid0, pid1, ...]
        movies = utm[user]
        for m in movies:
            # label is the kmeans++-cluster number
            label = mtLabel[m]
            labelNums[label-1] += 1

        # 0: score, 1: helpfulness, 2: subjectivity, 3: kinds of movies
        # total dims: 3 + 2 + 1 + 10 = 16
        userData[user] = [feat, help, subjs, labelNums]

    print "GHOSTS:", len(ghosts)
    f = open('ghosts.pkl', 'wb')
    cPickle.dump(ghosts, f)
    f.close()

    print "num unknown users:", numUnknowns
    print "num users with data logged:", len(userData)
    f = open(args.output, 'wb')
    cPickle.dump(userData, f)
    f.close()
    
# blur
# fuzzy hash or something

# double-divide '//' is integer division in __future__ div

#def kdtree():
# do LSH (Locality-sensitive Hashing) instead of kd-trees
# because 16-dims is a lot of dims for just 1.2+M data points
# ref: http://web.iitd.ac.in/~sumeet/Slaney2008-LSHTutorial.pdf
def lsh(M=3):
    # pick M random vectors
    # gaussian random
    randGauss = np.random.normal

    hyperplanes = []
    for x in xrange(M):
        hyperPlane = np.zeros(NUM_DIMS)
        for i in xrange(NUM_DIMS):
            hyperPlane[i] = randGauss()
        hyperplanes.append(hyperPlane)

    print "got M=%d hyperplanes" % M
    print hyperplanes
    print "\n=====================\n\n"

    if args.haveDataVecs:
        f = open(args.datavec, 'rb')
        userToDataVecs = cPickle.load(f)
        f.close()
    else:
        f = open(args.data, 'rb')
        userData = cPickle.load(f)
        f.close()

        print "num data:", len(userData)

        userToDataVecs = {}
        #hash everything
        for user in userData:
            data = userData[user]
            dataVec = np.array([ data[0][0], data[0][1][0], data[0][1][1], 
                                 data[0][2], data[0][3], data[0][4],
                                 data[0][5],
                                 data[1][0], data[1][1], 
                                 data[2], 
                                 data[3][0], data[3][1], data[3][2],data[3][3],
                                 data[3][4], data[3][5], data[3][6],data[3][7],
                                 data[3][8], data[3][9] ])
            userToDataVecs[user] = dataVec

        f = open(args.datavec, 'wb')
        cPickle.dump(userToDataVecs, f)
        f.close()

    userToHashed = {}
    hashSets = {}
    n = len(hyperplanes)
    for user in userToDataVecs:
        dataVec = userToDataVecs[user]
        # dot product with random vecs
        hash = ''
        for i in xrange(n):
            hPlane = hyperplanes[i]
            dotPdt = np.dot(hPlane, dataVec)
            if dotPdt >= 0:
                hash += '1'
            else:
                hash += '0'

        userToHashed[user] = hash
        try:
            hashSets[hash] += 1
        except:
            hashSets[hash] = 1

    print "###############"
    print hashSets
    print "###############"


    f = open(args.hashdata, 'wb')
    cPickle.dump(hashSets, f)
    f.close()

    print "num hash sets", len(hashSets)
    for h in hashSets:
        print "hashSet", h, " len:", hashSets[h]
    print "========"


def getUserDataSubset():
    f = open(args.data, 'rb')
    userData = cPickle.load(f)
    f.close()

    subset = {}
    i = 0
    for user in userData:
        if i % 91993 == 0:
            subset[user] = userData[user]
        i += 1

    f = open("subset.pkl", 'wb')
    cPickle.dump(subset, f)
    f.close()
        

def normalizeData():
    # get min max of all 20 features
    f = open(args.data, 'rb')
    userData = cPickle.load(f)
    f.close()

    numUsers = len(userData)
    d0, d1 = np.zeros(numUsers), np.zeros(numUsers)
    d2, d3 = np.zeros(numUsers), np.zeros(numUsers)
    d4, d5 = np.zeros(numUsers), np.zeros(numUsers)
    d6, d7 = np.zeros(numUsers), np.zeros(numUsers)
    d8, d9 = np.zeros(numUsers), np.zeros(numUsers)
    d10, d11 = np.zeros(numUsers), np.zeros(numUsers)
    d12, d13 = np.zeros(numUsers), np.zeros(numUsers)
    d14, d15 = np.zeros(numUsers), np.zeros(numUsers)
    d16, d17 = np.zeros(numUsers), np.zeros(numUsers)
    d18, d19 = np.zeros(numUsers), np.zeros(numUsers)
    i = 0
    for user in userData:
        data = userData[user]
        d0[i] = data[0][0]
        d1[i] = data[0][1][0]
        d2[i] = data[0][1][1]
        d3[i] = data[0][2]
        d4[i] = data[0][3]
        d5[i] = data[0][4]
        d6[i] = data[0][5]
        d7[i] = data[1][0]
        d8[i] = data[1][1]
        d9[i] = data[2]
        d10[i] = data[3][0]
        d11[i] = data[3][1]
        d12[i] = data[3][2]
        d13[i] = data[3][3]
        d14[i] = data[3][4]
        d15[i] = data[3][5]
        d16[i] = data[3][6]
        d17[i] = data[3][7]
        d18[i] = data[3][8]
        d19[i] = data[3][9]
        i += 1
        
    # get min-maxes
    d_mins = [0 for x in xrange(20)]
    d_maxs = [0 for x in xrange(20)]
    d_mins[0], d_maxs[0] = np.nanmin(d0), np.nanmax(d0)
    d_mins[1], d_maxs[1] = np.nanmin(d1), np.nanmax(d1)
    d_mins[2], d_maxs[2] = np.nanmin(d2), np.nanmax(d2)
    d_mins[3], d_maxs[3] = np.nanmin(d3), np.nanmax(d3)
    d_mins[4], d_maxs[4] = np.nanmin(d4), np.nanmax(d4)
    d_mins[5], d_maxs[5] = np.nanmin(d5), np.nanmax(d5)
    d_mins[6], d_maxs[6] = np.nanmin(d6), np.nanmax(d6)
    d_mins[7], d_maxs[7] = np.nanmin(d7), np.nanmax(d7)
    d_mins[8], d_maxs[8] = np.nanmin(d8), np.nanmax(d8)
    d_mins[9], d_maxs[9] = np.nanmin(d9), np.nanmax(d9)
    d_mins[10], d_maxs[10] = np.nanmin(d10), np.nanmax(d10)
    d_mins[11], d_maxs[11] = np.nanmin(d11), np.nanmax(d11)
    d_mins[12], d_maxs[12] = np.nanmin(d12), np.nanmax(d12)
    d_mins[13], d_maxs[13] = np.nanmin(d13), np.nanmax(d13)
    d_mins[14], d_maxs[14] = np.nanmin(d14), np.nanmax(d14)
    d_mins[15], d_maxs[15] = np.nanmin(d15), np.nanmax(d15)
    d_mins[16], d_maxs[16] = np.nanmin(d16), np.nanmax(d16)
    d_mins[17], d_maxs[17] = np.nanmin(d17), np.nanmax(d17)
    d_mins[18], d_maxs[18] = np.nanmin(d18), np.nanmax(d18)
    d_mins[19], d_maxs[19] = np.nanmin(d19), np.nanmax(d19)

    min_max = (d_mins, d_maxs)
    f = open('min_max.pkl', 'wb')
    cPickle.dump(min_max, f)
    f.close()

    # normalize that shit!
    normalizedData = {}
    for user in userData:
        data = userData[user]
        nData = [(data[0][0] / d_maxs[0], 
                  (data[0][1][0] / d_maxs[1], data[0][1][1] / d_maxs[2]),
                  data[0][2] / d_maxs[3], data[0][3] / d_maxs[4],
                  data[0][4] / d_maxs[5], data[0][5] / d_maxs[6]),
                  (data[1][0] / d_maxs[7], data[1][1] / d_maxs[8]),
                 data[2] / d_maxs[9],
                 (data[3][0] / d_maxs[10], data[3][1] / d_maxs[11],
                  data[3][2] / d_maxs[12], data[3][3] / d_maxs[13],
                  data[3][4] / d_maxs[14], data[3][5] / d_maxs[15],
                  data[3][6] / d_maxs[16], data[3][7] / d_maxs[17],
                  data[3][8] / d_maxs[18], data[3][9] / d_maxs[19])]
        normalizedData[user] = nData

    f = open('normalized_ALL.pkl', 'wb')
    cPickle.dump(normalizedData, f)
    f.close()

def main():
    t = time()
    if args.getuserdata:
        getUserScoreFeats()
    if args.kdtree:
        kdtree()

    if args.subset:
        getUserDataSubset()

    if args.lsh:
        lsh()

    if args.normalize:
        normalizeData()

    print "TIME:", time() - t

if __name__ == '__main__':
    main()

