from __future__ import division
import argparse
import cPickle
import pprint
from textblob.classifiers import NaiveBayesClassifier
from textblob_aptagger import PerceptronTagger
from textblob import TextBlob

USEFUL_POS_TAGS = ['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'PRP', 'RB', 'PRP$', 'RB', 'RBR', 'RBS','VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

parser = argparse.ArgumentParser()
parser.add_argument('--makeTrainers', action='store_true')
parser.add_argument('--makeClassifier', action='store_true')
parser.add_argument('-o', help='objective training set')
parser.add_argument('-s', help='subjective training set')
parser.add_argument('-u', help='users data')
parser.add_argument('-po', help='P objective')
parser.add_argument('-ps', help='P subjective')
parser.add_argument('-t', help='own training set. own labeled. 1 is subj')
parser.add_argument('--updateClassifier', action='store_true')

args = parser.parse_args()

def getPxbj(pobj, psubj):
    Pobj = cPickle.load(open(pobj, 'rb'))[0]
    Psubj = cPickle.load(open(psubj, 'rb'))[0]
    return Pobj, Psubj

# generate user vectors -> convert review to objective/ subjective ratio

def naiveBayesClassifier(obj, sub, corpusSize=5000):
    print "rolling own naive bayes thing..."
    f = open(obj, 'r')
    trainingObjs = f.read()
    f.close()
    f = open(sub, 'r')
    trainingSubs = f.read()
    f.close()

    # parse training set
    trainingSets = [trainingObjs, trainingSubs]
    totalUniques = 0 # num unique words
    i = 0
    numWords = [0, 0] # num obj words, num sub words (non-unique)
    tokenSets = [{}, {}] # [obj tokens, sub tokens]

    tagger = PerceptronTagger()

    # objective set
    train = trainingSets[0]
    tokens = tokenSets[0]
    # tag out useful words: verbs, nouns, adjectives
    for word, tag in TextBlob(train, pos_tagger=tagger).tags:
        if tag in USEFUL_POS_TAGS:
            if word.isalpha():
                numWords[0] += 1
                if word in tokens:
                    tokens[word] += 1
                else:
                    tokens[word] = 0
                    totalUniques += 1
    # subjective set
    train = trainingSets[1]
    tokens = tokenSets[1]
    # tag out useful words: verbs, nouns, adjectives
    for word, tag in TextBlob(train, pos_tagger=tagger).tags:
        if tag in USEFUL_POS_TAGS:
            if word.isalpha():
                numWords[1] += 1
                if word in tokens:
                    tokens[word] += 1
                else:
                    tokens[word] = 0
                    totalUniques += 1

    # total words
    totalWords = numWords[0] + numWords[1]
    Pobj = numWords[0] / totalWords
    Psubj = numWords[1] / totalWords

    f = open(args.po, 'wb')
    cPickle.dump([Pobj], f)
    f.close()
    f = open(args.ps, 'wb')
    cPickle.dump([Psubj], f)
    f.close()

    # calculate smoothed probabilities
    objProbs, subProbs = {}, {}
    # obj tokens
    tokens = tokenSets[0]
    for w in tokens:
        objProbs[w] = (tokens[w] + 1) / (numWords[0] + 5000)
    # sub tokens
    tokens = tokenSets[1]
    for w in tokens:
        subProbs[w] = (tokens[w] + 1) / (numWords[1] + 5000)

    print "Done training."
    f = open('objProbs.pkl', 'wb')
    cPickle.dump(objProbs, f)
    f.close()
    f = open('subProbs.pkl', 'wb')
    cPickle.dump(subProbs, f)
    f.close()

    return Pobj, Psubj


# want to classify 'text'
def classify(obj, sub, Pobj, Psubj, granular=True):
    # saved classifiers
    f = open(obj, 'rb')
    objProbs = cPickle.load(f)
    f.close()
    f = open(sub, 'rb')
    subProbs = cPickle.load(f)
    f.close()
        
    f = open(args.s, 'r')
    lines = f.readlines()
    f.close()
    #f = open(args.o, 'r')
    #lines2 = f.readlines()
    #f.close()

    print "test set results"
    nowClassify(lines, objProbs, subProbs, Pobj, Psubj, granular)
    #print "objective test set results"
    #nowClassify(lines2, objProbs, subProbs, Pobj, Psubj)

# granular makes larger training files
def nowClassify(lines, objProbs, subProbs, Pobj, Psubj, granular):
    # true == subjective
    classed = []
    subjC, objC = 0, 0

    if granular:
        print "heylus"
        granularLines = []
        for line in lines:
            # split review into sentences
            a = (' ').join(line.replace(',', '').split()).replace('?','\n').replace('!','\n').replace('.','\n')
            a = a.split('\n')
            for x in a:
                if x:
                    granularLines.append(x)
        lines = granularLines

        sFile = open('update5000_subj.txt', 'w')
        oFile = open('update5000_obj.txt', 'w')

    rFile = open('subjResults_ALL.txt', 'w')

    for line in lines:
        # tokenize line
        if not granular:
            line = line.replace(',', '')
        sentence = line.split(' ')
        objectivity, subjectivity = Pobj, Psubj
        # sum probabilities of being objective
        # sum probabilities of being subjective
        for word in sentence:
            if word in objProbs:
                objectivity *= objProbs[word]
            if word in subProbs:
                subjectivity *= subProbs[word]
        # compare sums to classify
        classed.append(subjectivity > objectivity)

        # TODO check <=
        if (subjectivity <= objectivity):
            if granular:
                sFile.write('1%s\n' % (' ').join(sentence))
            subjC += 1
            rFile.write('1')
        else:
            if granular:
                oFile.write('0%s\n' % (' ').join(sentence))
            objC += 1
            rFile.write('0')

    rFile.write('\n')
    rFile.close()

    if granular:
        sFile.close()
        oFile.close()

    print "Subj lines: %d, Obj lines %d" % (subjC, objC)

def makeSubjectivityTrainers(sub, obj, block=True, ownSet=True, set=''):

    print "Making training set..."
    rawObjSet, rawSubSet = [], []

    if ownSet:
        f = open(set, 'r')
        trainingSet = f.readlines()
        for t in trainingSet:
            if t[0] == '1':
                rawSubSet.append(t[1:])
            else:
                rawObjSet.append(t[1:])
    else:
        f = open(obj, 'r')
        rawObjSet = f.readlines()
        f.close()
        f = open(sub, 'r')
        rawSubSet = f.readlines()
        f.close()

    if block:
        print "Num Objs: %d, Num Subjs: %d" % (len(rawObjSet), len(rawSubSet))
        testObjFile = open("trainingObj.txt", 'wb')
        testSubFile = open("trainingSub.txt", 'wb')
        for obj in rawObjSet:
            sent = unicode(obj[:-1].replace(',', ''), errors='ignore')
            testObjFile.write('%s ' % sent)
        for sub in rawSubSet:
            sent = unicode(sub[:-1].replace(',', ''), errors='ignore')
            testSubFile.write('%s ' % sent)
        testObjFile.close()
        testSubFile.close()
    else:
        rawSets = [rawObjSet, rawSubSet]
        type = ['obj', 'sub']
        testSetFile = open("objsub.csv", "wb")
        i = 0
        for set in rawSets:
            for sample in set:
                # since it is a csv file, cannot have commas in sentence
                sent = unicode(sample[:-1].replace(',', ''), errors='ignore')
                testSetFile.write("%s,%s\n" % (sent, type[i]))
            i += 1
        testSetFile.close()

if __name__ == '__main__':
    if args.makeTrainers:
        makeSubjectivityTrainers(args.s, args.o, ownSet=True, set=args.t)
    if args.makeClassifier:
        pObj, pSubj = naiveBayesClassifier('trainingObj.txt', 
                                           'trainingSub.txt')
    else:
        pObj, pSubj = getPxbj(args.po, args.ps)

    print

    if args.updateClassifier:
        classify('objProbs.pkl', 'subProbs.pkl', pObj, pSubj, granular=True)
    else:
        classify('objProbs.pkl', 'subProbs.pkl', pObj, pSubj, granular=False)

    print "We done now whad"
    exit(0)
