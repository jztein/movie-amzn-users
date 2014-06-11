'''
USAGE:
$ python labelMovies.py -g fineC.pkl -c kmeansK10.pkl -o pidToKmeans.pkl
number of labeledMovies: 207533
'''
import argparse, cPickle

parser = argparse.ArgumentParser()
# fineC.pkl
parser.add_argument('-g', help='grouped movies (movies labeled by hash)')
# kmeansK10.pkl
parser.add_argument('-c', help='kmeans++ clusters of movies')
#pidToKmeans.pkl
parser.add_argument('-o', help='outfile = labeled movies by cluster')

args = parser.parse_args()

def labelMovies():
    # 1) movies are currently grouped into connected graphs,
    # where edges are users. So an edge between movies means that
    # at least one user rated that movie
    # 2) the movie groups were then split into rated-above-avg and
    # otherwise groups
    # 3) kmeans++ was then used to cluster these finer groups
    # 4) now we want to label each movie by its kmeans++ cluster

    # k = 10

    # in the fine-groups file, we use the file where the
    # key is the movie, and the value is the group number
    f = open(args.g, 'rb')
    fineGroups = cPickle.load(f)
    f.close()

    # the kmeans file is a list of size 10, each element is
    # a list of the fine-groups in that cluster
    f = open(args.c, 'rb')
    kmeansClusters = cPickle.load(f)
    f.close()

    labeledMovies = {}
    for kth in kmeansClusters:
        cluster = kmeansClusters[kth]
        for fineGroup in cluster:
            movies = fineGroups[fineGroup]
            for movie in movies:
                labeledMovies[movie] = kth

    f = open(args.o, 'wb')
    cPickle.dump(labeledMovies, f)
    f.close()

    print "number of labeledMovies:", len(labeledMovies) # 207533

if __name__ == '__main__':
    labelMovies()
