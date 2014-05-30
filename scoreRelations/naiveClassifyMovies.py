'''
EIGHT classes of movies:
(1a) appealing, (1b) unappealing;
- means, skewness
(2a) uniting, (2b) divisive;
- variance, kurtosis
(3a) blockbuster, (3b) arthouse/ unpopular
- size

Could be 2**5 = 32 classes (if we consider SKEW, KURTOSIS)
'''

import argparse
import cPickle
from scipy import stats
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--mts')
parser.add_argument('--naive', action='store_true')
parser.add_argument('--look', action='store_true')

args = parser.parse_args()

def lookAtNaive():
    for i in xrange(1, 9):
        f = open('class%dpid.pkl' % i, 'rb')
        curClass = cPickle.load(f)
        print len(curClass)
        print curClass[:5]
        f.close()

def naiveClassify():
    f = open(args.mts, 'rb')
    mts = cPickle.load(f)
    f.close()

    size = len(mts)
    #size = 5
    print "numMovies: %d" % len(mts)

    sizes = np.zeros(size)
    means = np.zeros(size)
    kurs = np.zeros(size)
    skews = np.zeros(size)
    vars = np.zeros(size)
    pids = np.zeros(size)

    i = 0
    for movie in mts:
        pids[i] = movie
        scores = mts[movie]
        s = stats.describe(scores)

        sizes[i] = s[0]
        means[i] = s[2]
        vars[i] = s[3]
        skews[i] = s[4]
        kurs[i] = s[5]

        i += 1

        #if i <= 5:
        #    print s[0], s[2], s[3], s[4], s[5]

    # PROBLEM: this is just getting 1 and 0's?

    # get classification boundaries # (a) criteria
    meanSize = np.mean(sizes[~np.isnan(sizes) == True]) # high
    meanMean = np.mean(means[~np.isnan(means) == True]) # high
    meanVar = np.mean(vars[~np.isnan(vars) == True])   # low
    meanSkew = np.mean(skews[~np.isnan(skews) == True]) # high
    meanKur = np.mean(kurs[~np.isnan(kurs) == True])   # low
        
    # no point using numpy arrays since not fixed size, and append
    # needs to reallocate and copy array every time
    class1, class2, class3, class4 = [], [], [], []
    class5, class6, class7, class8 = [], [], [], []
    class9, class10, class11, class12 = [], [], [], []
    class13, class14, class15, class16 = [], [], [], []
    class17, class18, class19, class20 = [], [], [], []
    class21, class22, class23, class24 = [], [], [], []
    class25, class26, class27, class28 = [], [], [], []
    class29, class30, class31, class32 = [], [], [], []
    for i in xrange(size):
        # classify
        # a: mean, b: skew, c: var, d: kurtosis, e: size
        if means[i] > meanMean:# and skews[i] > meanSkew:
            if skews[i] > meanSkew:
                if vars[i] < meanVar:# and kurs[i] < meanKur:
                    if kurs[i] < meanKur:
                        # 1a2a3a4a5a
                        if sizes[i] > meanSize:
                            class1.append(pids[i])
                        # 1a2a3a4a5b
                        else:
                            class2.append(pids[i])
                    else:
                        # 1a2a3a4b5a
                        if sizes[i] > meanSize:
                            class3.append(pids[i])
                        # 1a2a3a4b5b
                        else:
                            class4.append(pids[i])
                else:
                    if kurs[i] < meanKur:
                        # 1a2a3b4a5a
                        if sizes[i] > meanSize:
                            class5.append(pids[i])
                        # 1a2a3b4a5b
                        else:
                            class6.append(pids[i])
                    else:
                        # 1a2a3b4b5a
                        if sizes[i] > meanSize:
                            class7.append(pids[i])
                        # 1a2a3b4b5b
                        else:
                            class8.append(pids[i])
            else:
                if vars[i] < meanVar:# and kurs[i] < meanKur:
                    if kurs[i] < meanKur:
                        # 1a2b3a4a5a
                        if sizes[i] > meanSize:
                            class9.append(pids[i])
                        # 1a2b3a4a5b
                        else:
                            class10.append(pids[i])
                    else:
                        # 1a2b3a4b5a
                        if sizes[i] > meanSize:
                            class11.append(pids[i])
                        # 1a2b3a4b5b
                        else:
                            class12.append(pids[i])
                else:
                    if kurs[i] < meanKur:
                        # 1a2b3b4a5a
                        if sizes[i] > meanSize:
                            class13.append(pids[i])
                        # 1a2b3b4a5b
                        else:
                            class14.append(pids[i])
                    else:
                        # 1a2b3b4b5a
                        if sizes[i] > meanSize:
                            class15.append(pids[i])
                        # 1a2b3b4b5b
                        else:
                            class16.append(pids[i])
        else:
            if skews[i] > meanSkew:
                if vars[i] < meanVar:# and kurs[i] < meanKur:
                    if kurs[i] < meanKur:
                        # 1a2a3a4a5a
                        if sizes[i] > meanSize:
                            class17.append(pids[i])
                        # 1a2a3a4a5b
                        else:
                            class18.append(pids[i])
                    else:
                        # 1a2a3a4b5a
                        if sizes[i] > meanSize:
                            class19.append(pids[i])
                        # 1a2a3a4b5b
                        else:
                            class20.append(pids[i])
                else:
                    if kurs[i] < meanKur:
                        # 1a2a3b4a5a
                        if sizes[i] > meanSize:
                            class21.append(pids[i])
                        # 1a2a3b4a5b
                        else:
                            class22.append(pids[i])
                    else:
                        # 1a2a3b4b5a
                        if sizes[i] > meanSize:
                            class23.append(pids[i])
                        # 1a2a3b4b5b
                        else:
                            class24.append(pids[i])
            else:
                if vars[i] < meanVar:# and kurs[i] < meanKur:
                    if kurs[i] < meanKur:
                        # 1b2b3a4a5a
                        if sizes[i] > meanSize:
                            class25.append(pids[i])
                        # 1b2b3a4a5b
                        else:
                            class26.append(pids[i])
                    else:
                        # 1b2b3a4b5a
                        if sizes[i] > meanSize:
                            class27.append(pids[i])
                        # 1b2b3a4b5b
                        else:
                            class28.append(pids[i])
                else:
                    if kurs[i] < meanKur:
                        # 1b2b3b4a5a
                        if sizes[i] > meanSize:
                            class29.append(pids[i])
                        # 1b2b3b4a5b
                        else:
                            class30.append(pids[i])
                    else:
                        # 1b2b3b4b5a
                        if sizes[i] > meanSize:
                            class31.append(pids[i])
                        # 1b2b3b4b5b
                        else:
                            class32.append(pids[i])


    print meanMean, meanVar, meanSize, meanKur, meanSkew
    print len(class1), len(class2), len(class3), len(class4)
    print len(class5), len(class6), len(class7), len(class8)
    print len(class9), len(class10), len(class11), len(class12)
    print len(class13), len(class14), len(class15), len(class16)
    print len(class17), len(class18), len(class19), len(class20)
    print len(class21), len(class22), len(class23), len(class24)
    print len(class25), len(class26), len(class27), len(class28)
    print len(class29), len(class30), len(class31), len(class32)
    '''
    print class1
    print class2
    print class3
    print class4
    print class5
    print class6
    print class7
    print class8
    '''

    # document this shit
    f = open('class1pid.pkl', 'wb')
    cPickle.dump(class1, f)
    f.close()
    f = open('class2pid.pkl', 'wb')
    cPickle.dump(class2, f)
    f.close()
    f = open('class3pid.pkl', 'wb')
    cPickle.dump(class3, f)
    f.close()
    f = open('class4pid.pkl', 'wb')
    cPickle.dump(class4, f)
    f.close()
    f = open('class5pid.pkl', 'wb')
    cPickle.dump(class5, f)
    f.close()
    f = open('class6pid.pkl', 'wb')
    cPickle.dump(class6, f)
    f.close()
    f = open('class7pid.pkl', 'wb')
    cPickle.dump(class7, f)
    f.close()
    f = open('class8pid.pkl', 'wb')
    cPickle.dump(class8, f)
    f.close()

    f = open('class9pid.pkl', 'wb')
    cPickle.dump(class9, f)
    f.close()
    f = open('class10pid.pkl', 'wb')
    cPickle.dump(class10, f)
    f.close()
    f = open('class11pid.pkl', 'wb')
    cPickle.dump(class11, f)
    f.close()
    f = open('class12pid.pkl', 'wb')
    cPickle.dump(class12, f)
    f.close()
    f = open('class13pid.pkl', 'wb')
    cPickle.dump(class13, f)
    f.close()
    f = open('class14pid.pkl', 'wb')
    cPickle.dump(class14, f)
    f.close()
    f = open('class15pid.pkl', 'wb')
    cPickle.dump(class15, f)
    f.close()
    f = open('class16pid.pkl', 'wb')
    cPickle.dump(class16, f)
    f.close()

    f = open('class17pid.pkl', 'wb')
    cPickle.dump(class17, f)
    f.close()
    f = open('class18pid.pkl', 'wb')
    cPickle.dump(class18, f)
    f.close()
    f = open('class19pid.pkl', 'wb')
    cPickle.dump(class19, f)
    f.close()
    f = open('class20pid.pkl', 'wb')
    cPickle.dump(class20, f)
    f.close()
    f = open('class21pid.pkl', 'wb')
    cPickle.dump(class21, f)
    f.close()
    f = open('class22pid.pkl', 'wb')
    cPickle.dump(class22, f)
    f.close()
    f = open('class23pid.pkl', 'wb')
    cPickle.dump(class23, f)
    f.close()
    f = open('class24pid.pkl', 'wb')
    cPickle.dump(class24, f)
    f.close()

    f = open('class25pid.pkl', 'wb')
    cPickle.dump(class25, f)
    f.close()
    f = open('class26pid.pkl', 'wb')
    cPickle.dump(class26, f)
    f.close()
    f = open('class27pid.pkl', 'wb')
    cPickle.dump(class27, f)
    f.close()
    f = open('class28pid.pkl', 'wb')
    cPickle.dump(class28, f)
    f.close()
    f = open('class29pid.pkl', 'wb')
    cPickle.dump(class29, f)
    f.close()
    f = open('class30pid.pkl', 'wb')
    cPickle.dump(class30, f)
    f.close()
    f = open('class31pid.pkl', 'wb')
    cPickle.dump(class31, f)
    f.close()
    f = open('class32pid.pkl', 'wb')
    cPickle.dump(class32, f)
    f.close()

if __name__ == '__main__':
    print "Jeu"
    if args.naive:
        naiveClassify()
    elif args.look:
        lookAtNaive()

    exit()
