import argparse
from zlib import adler32
from time import time

LEN_PID = len('product/productId: ')
LEN_TITLE = len('product/title: ')
LEN_PRICE = len('product/price: ')
LEN_UID = len('review/userId: ')
LEN_PROFILE = len('review/profileName: ')
LEN_HELP = len('review/helpfuleness:')
LEN_SCORE = len('review/score: ')
LEN_TIME = len('review/time: ')
LEN_SUMMARY = len('review/summary: ')
LEN_TEXT = len('review/text: ')

argParser = argparse.ArgumentParser(description="export mode user reviews")
argParser.add_argument('input', help='input txt file name')
argParser.add_argument('output', help='output txt file name')
# indices = find(all(:, 2) == M), M is mode
argParser.add_argument('indices', help='indices of sections this uid')

args = argParser.parse_args()

'''
Format:
PID, helpN, helpD, score
Summary
Text
'''

def getIndices():
    idxLines = open(args.indices, 'r').readlines()
    indexes = [int(i) for i in idxLines]
    return indexes

def parseSection(section):
    uid = section[3][LEN_UID:-1]
    if uid == 'unknown' or uid != "A16CZRQL23NOIW":
        return None

    pid = section[0][LEN_PID:-1]

    #title = section[1][LEN_TITLE: -1]
    #price = section[2][LEN_PRICE:-1]
    #profile = section[4][LEN_PROFILE:-1]

    helpfulness = section[5][LEN_HELP:-1].split('/')
    # help numerator / denominator
    helpN = helpfulness[0]
    helpD = helpfulness[1]

    score = section[6][LEN_SCORE:-1]

    #time = section[7][LEN_TIME:-1]
    summary = section[8][LEN_SUMMARY:-1]
    text = section[9][LEN_TEXT:-1]

    outFile.write('%s, %s, %s, %s\n%s\n%s\n' % (pid, helpN, helpD, score,
                                                summary, text))

def parse():
    print "Reading input file..."
    txtFile = open(args.input, 'r')
    lines = txtFile.readlines()
    leftOver = len(lines) % 11
    if leftOver:
        print 'WARNING <= ignoring last section because it is not complete'
    # sections means one complete unit of data including the extra endline
    numSections = len(lines) / 11

    # no point because unknowns were not counted into indices
    #print "Getting indices..."
    #indexes = getIndices()
    #print indexes
    print "Parsing sections..."
    for s in xrange(numSections):
        s11 = s*11
        section = lines[s11 : s11+11]
        parseSection(section)

if __name__ == '__main__':
    t = time()
    outFile = open(args.output, 'w')
    parse()
    print "Time taken:", time() - t
    outFile.close()
    exit()
