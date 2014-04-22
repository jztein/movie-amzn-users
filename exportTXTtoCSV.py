import argparse

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

argParser = argparse.ArgumentParser(description="export Movies&TV.txt to csv")
argParser.add_argument('--txt', '-t', nargs=1, required=True, help='txt file name')
argParser.add_argument('--csv', '-c', nargs=1, required=True, help='csv file name')

args = argParser.parse_args()

def setupCSVfile(csvFile):
    csvFile.write('pid,uid,helpN,helpD,score,time\n')

# AN = alphanumeric e.g. B0001Z3TLQ
def transANtoASCII(id):
    return ''.join([str(ord(x)) for x in id])

def parseSection(section):
    productID = section[0][LEN_PID:-1]
    productID = transANtoASCII(productID)

    title = section[1][LEN_TITLE: -1]
    price = section[2][LEN_PRICE:-1]
    userID = transANtoASCII(section[3][LEN_UID:-1])
    profile = section[4][LEN_PROFILE:-1]

    helpfulness = section[5][LEN_HELP:-1].split('/')
    helpNumerator = int(helpfulness[0])
    helpDenominator = int(helpfulness[1])

    score = float(section[6][LEN_SCORE:-1])

    time = int(section[7][LEN_TIME:-1])
    summary = section[8][LEN_SUMMARY:-1]
    text = section[9][LEN_TEXT:-1]

    csvFile.write('%s,%s,%d,%d,%f,%d\n' % (productID,userID,helpNumerator
                                        ,helpDenominator,score,time))

    return {'pid':productID, 'title':title, 'price':price, 'uid':userID,\
            'profile':profile, 'helpN':helpNumerator, \
            'helpD':helpDenominator, 'score':score, 'time':time, \
            'sum':summary, 'text':text}

# 10+1 lines

def parse():
    txtFile = open(args.txt[0], 'r')
    lines = txtFile.readlines()
    leftOver = len(lines) % 11
    if leftOver:
        print 'WARNING <= ignoring last section because it is not complete'
    # sections means one complete unit of data including the extra endline
    numSections = len(lines) / 11
    for s in xrange(numSections):
        s11 = s*11
        section = lines[s11 : s11+11]
        parseSection(section)

if __name__ == '__main__':
    csvFile = open(args.csv[0], 'w')
    setupCSVfile(csvFile)
    parse()
    csvFile.close()
    exit()
