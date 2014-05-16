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
def classify(obj, sub, Pobj, Psubj):
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
    f = open(args.o, 'r')
    lines2 = f.readlines()
    f.close()

    print "subjective test set results"
    nowClassify(lines, objProbs, subProbs, Pobj, Psubj)
    print "objective test set results"
    nowClassify(lines2, objProbs, subProbs, Pobj, Psubj)

def nowClassify(lines, objProbs, subProbs, Pobj, Psubj):
    # true == subjective
    classed = []
    subjC, objC = 0, 0
    for line in lines:
        # tokenize line
        sentence = line.replace(',', '').split(' ')
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
        if (subjectivity > objectivity):
            subjC += 1
        else:
            objC += 1

    print subjC, objC

if __name__ == '__main__':
    if args.makeTrainers:
        makeSubjectivityTrainers(args.s, args.o)
    if args.makeClassifier:
        pObj, pSubj = naiveBayesClassifier('trainingObj.txt', 
                                           'trainingSub.txt')
    else:
        pObj, pSubj = getPxbj(args.po, args.ps)

    classify('objProbs.pkl', 'subProbs.pkl', pObj, pSubj)

    print "We done now whad"
    exit(0)
