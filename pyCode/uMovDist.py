import argparse
import numpy as np
from scipy import misc
import pylab
import matplotlib.pyplot as plt
import matplotlib.colors as color

parser = argparse.ArgumentParser()
parser.add_argument('-c')

args = parser.parse_args()

csvFile = open(args.c, 'r')
allLines = csvFile.readlines()
header = allLines[0]

numLines = len(allLines)
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
