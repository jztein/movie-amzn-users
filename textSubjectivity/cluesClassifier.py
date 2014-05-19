'''

Output is in shredded.txt. Some problems with it.
Hand-checked first-2600 lines of shredded.txt for correct subjectivity label.
Now in train2600.txt

'''
from __future__ import division
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-w', help='wiebe lexicon')
parser.add_argument('-u', help='text to classify and use to update')

args = parser.parse_args()

def parseLexicon(lexiconFile):
    f = open(lexiconFile, 'r')
    lines = f.readlines()
    f.close()

    subjWords, objWords = {}, {}
    for line in lines:
        parts = line.split()
        subjectivity = parts[0][5] # after 'type='
        word = parts[2][6:] # after 'word1='
        if subjectivity == 'w':
            # weaksubj is more objective
            if word in objWords:
                objWords[word] += 4
            else:
                objWords[word] = 1
        else:
            # strongsubj is more subjective
            if word in subjWords:
                subjWords[word] += 4
            else:
                subjWords[word] = 1

    return subjWords, objWords

def classify(subjWords, objWords, fileToClassify):
    f = open(fileToClassify, 'r')
    reviews = f.readlines()
    f.close()
    
    f = open('newTrainingFile.txt', 'w')
    sF = open('newSubjTrain.txt', 'w')
    oF = open('newObjTrain.txt', 'w')

    for r in reviews:
        r = r.replace('?', '\n').replace('.', '\n').replace('!', '\n')
        lines = r.split('\n')
        
        for l in lines:
            words = (' '.join(l.split())).split()
            if not words:
                continue
            numSubjs, numObjs = 0, 0
            for word in words:
                if word in subjWords:
                    numSubjs += subjWords[word]
                elif word in objWords:
                    numObjs += objWords[word]
            if numSubjs < numObjs and len(words) > 4:
                # more objective line
                result = '0%s\n' % (' '.join(words))
                f.write(result)
                oF.write(result)
            else:
                # more subjective line
                result = '1%s\n' % (' '.join(words))
                sF.write(result)
                f.write(result)

    sF.close()
    oF.close()

if __name__ == '__main__':
    s, o = parseLexicon(args.w)
    classify(s, o, args.u)

    exit()
