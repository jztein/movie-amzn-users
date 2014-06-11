from __future__ import division
import argparse, cPickle, csv

parser = argparse.ArgumentParser()
parser.add_argument('--csv', help='all data csv')
parser.add_argument('-o', help='file to output')

args = parser.parse_args()

def calcHelpStats(helpNDs):
    # helpNDs is a list of pairs (help_numerator, help_denominator)
    # stats = helpfulnessRatio, number of people who rated helpfulness
    totalN, totalD = 0, 0
    for pair in helpNDs:
        totalN += pair[0]
        totalD += pair[1]
    if totalD == 0:
        return (0, 0)
    return (totalN/totalD, totalD)

def getHelp():
    f = open(args.csv, 'r')
    allData = csv.reader(f)

    i = 0

    userToHelpND = {}

    for data in allData:
        if i == 0:
            i += 1
            # header
            continue

        uid = int(data[1])

        try:
            userToHelpND[uid].append( (int(data[2]), int(data[3])) )
        except:
            userToHelpND[uid] = [ (int(data[2]), int(data[3])) ]

    f.close()

    userToHelpStats = {}
    for user in userToHelpND:
        userToHelpStats[user] = calcHelpStats(userToHelpND[user])

    print "numUsers:", len(userToHelpStats)


    f = open(args.o, 'wb')
    cPickle.dump(userToHelpStats, f)
    f.close()

if __name__ == '__main__':
    getHelp()
    exit()
