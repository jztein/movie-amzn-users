from __future__ import division
import argparse
import cPickle
import pprint
from textblob.classifiers import NaiveBayesClassifier
from textblob_aptagger import PerceptronTagger
from textblob import TextBlob

USEFUL_POS_TAGS = ['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'PRP', 'RB', 'PRP$', 'RB', 'RBR', 'RBS','VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

parser = argparse.ArgumentParser()
parser.add_argument('--training', action='store_true')
parser.add_argument('-o', help='objective training set')
parser.add_argument('-s', help='subjective training set')
parser.add_argument('-u', help='users data')

args = parser.parse_args()

# make training sets. here, sub and obj are raw text files of the samples
def makeSubjectivityTrainers(sub, obj, block=True):
    print "Making training set..."
    f = open(obj, 'r')
    rawObjSet = f.readlines()
    f.close()
    f = open(sub, 'r')
    rawSubSet = f.readlines()
    f.close()

    if block:
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

def makeClassifier(trainingFile):
    print "Making classifier..."
    return NaiveBayesClassifier(trainingFile, format='csv')

# user's overall subjective : objective ratio
# user's subjective : objective ratio for favorable reviews
# user's subjective : objective ratio for unhappy reviews

def classifyUserData(classifier):
    print "Classifying shit..."

    # 1. read user data
    uFile = open(args.u, 'r')
    data = uFile.readlines()
    uFile.close

    numReviews = int(len(data) / 3)
    helpN = [0 for x in xrange(numReviews)]
    helpD = [0 for x in xrange(numReviews)]
    scores = [0.0 for x in xrange(numReviews)]
    reviews = ['' for x in xrange(numReviews)]

    i = -1
    k = 0
    for line in data:
        i += 1
        if i == 0:
            # pid, helpfulness, score
            line = line.split()
            helpN[k] = line[1]
            helpD[k] = line[2]
            scores[k] = line[3]
        elif i == 2:
            # review
            i = -1
            reviews[k] = line[:-1]
            k += 1

    # 2. classify user data
    for review in reviews:
        print classifier.classify(review)
    
    # how averagely helpful

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

    '''
    # objective set
    train = trainingSets[0]
    words = train.split(' ')
    tokens = tokenSets[i]
    for w in words:
        if w.isalpha():
            numWords[i] += 1
            if w in tokens:
                tokens[w] += 1
            else:
                tokens[w] = 0
                totalUniques += 1
    i += 1

    # blegh
    train = trainingSets[1]
    words = train.split(' ')
    tokens = tokenSets[i]
    for w in words:
        if w.isalpha():
            numWords[i] += 1
            if w in tokens:
                tokens[w] += 1
            else:
                tokens[w] = 0
                totalUniques += 1

    '''            

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
    #makeSubjectivityTrainers(args.s, args.o)
    #depr? classifier = makeClassifier("objsub.csv")
    #depr? classifyUserData(classifier)

    pObj, pSubj = naiveBayesClassifier('trainingObj.txt', 'trainingSub.txt')
    classify('objProbs.pkl', 'subProbs.pkl', pObj, pSubj)

    print "We done now whad"
    exit(0)
