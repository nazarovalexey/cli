import sys
import re
from os.path import exists


#reg = re.compile("(^\s+|\s+$)")
#str = "  some string    ";
#print( str + "\n", end = "" )
#str_clear = re.sub("(^\s+|\s+$)", "", str)
#print( str_clear + "\n", end = "" )


# 5,123,819  ???:_start [/home/ykuznetsov/klish-2.1.3/bin/.libs/clish]
# 5,123,808  /opt/build/glibc/glibc-2.24/csu/../csu/libc-start.c:(below main) [/lib/x86_64-linux-gnu/libc-2.24.so]
# 5,120,471  /home/ykuznetsov/klish-2.1.3/bin/clish.c:main [/home/ykuznetsov/klish-2.1.3/bin/.libs/clish]

# exclusive profiling
# 680,674 (10.37%)  /opt/build/glibc/glibc-2.24/malloc/malloc.c:_int_malloc [/lib/x86_64-linux-gnu/libc-2.24.so]
# 417,920 ( 6.37%)  /opt/build/glibc/glibc-2.24/iconv/../iconv/skeleton.c:__gconv_transform_utf8_internal [/lib/x86_64-linux-gnu/libc-2.24.so]
# 400,032 ( 6.10%)  /opt/build/glibc/glibc-2.24/malloc/malloc.c:_int_free [/lib/x86_64-linux-gnu/libc-2.24.so]
# 382,308 ( 5.83%)  /opt/build/glibc/glibc-2.24/wcsmbs/mbrtowc.c:mbrtowc [/lib/x86_64-linux-gnu/libc-2.24.so]


str = "5,120,471  /home/ykuznetsov/klish-2.1.3/bin/clish.c:main [/home/ykuznetsov/klish-2.1.3/bin/.libs/clish]"


def printUsage():
    print("{}: <left_table> <right_table>".format( sys.argv[0] ))


def splitReportLine(line):
    line = re.sub(r"(^\s+|\s+$)", "", line)
    lineOr = line


    irs = re.findall(r"^([0-9\,]+)\s", line)
    if len(irs) != 1:
        print( "unknown syntax: '{}'".format(lineOr) )
        exit(2)
    else:
        irs = irs[0]
        irs = re.sub(r",", "", irs)
        line = re.sub(r"^[0-9\,]+\s", "", line)


    boo = bool(re.match(r"^\([^)]+\)\s", line))
    if not boo:
        print( "unknown syntax: '{}'".format(lineOr) )
        exit(2)
    else:
        line = re.sub(r"^\([^)]+\)\s", "", line)

    # may or may not exists
    module = re.findall(r"\s(\[[^\]]+\])$", line)
    if len(module) == 0:
        module = ''
    elif len(module) == 1:
        module = module[0]
        line = re.sub(r"\s\[[^\]]+\]$", "", line)
    else:
        print( "unknown syntax: '{}'".format(lineOr) )
        exit(2)
 

    line = re.sub(r"(^\s+|\s+$)", "", line)
    sf = re.split(":", line)
    if not len(sf) == 2:
        print( "unknown syntax: '{}'".format(lineOr) )
        exit(2)

    return [irs, sf[0], sf[1], module]




def readLines(fName):
    try:
        f = open(fName, 'r')
        fLines = f.readlines()
    except:
        printf("unable to open file '{}' for reading".format(fName))
        exit(3)

    return fLines
        
# [[irs, src, func, mod], ...]
def getReportArray(lines):
    rep = list()
    for line in lines:
        if not bool(re.match("^\s*$", line)):
            fields = splitReportLine(line)
            rep.append(fields)

    return rep

def getReportHash(arr):
    dic = {}
    for fields in arr:
        # [irs, src, func, mod]
        assert( len(fields) == 4 )
        irs = fields[0]
        src = fields[1]
        func = fields[2]
        mod = fields[3]

        key = src + ':' + func
        if key in dic:
            dic[key][0] = dic[key][0] + int(irs)
        else:
            dic[key] = [int(irs), mod]
    return dic


# [l.src l.func l.irs r.irs]
def getLeftIr(fields):
    return int(fields[2])


def main():
    if len(sys.argv) != 3:
        printUsage()
        exit(2)
    else:
        leftFile = sys.argv[1]
        rightFile = sys.argv[2]


    if 0 == exists(leftFile):
        print("unable to locate '{}' file".format(leftFile))
        exit(3)
    if 0 == exists(rightFile):
        print("unable to locate '{}' file".format(rightFile))
        exit(3)

    

    leftLines = readLines(leftFile)
    rightLines = readLines(rightFile)

    # we a going to make left auter join;
    # prepare assiciative array from right array

    leftArray = getReportArray(leftLines)
    rightArray = getReportArray(rightLines)

    leftHash = getReportHash(leftArray)
    rightHash = getReportHash(rightArray)

    # produle left outer join of the form:
    # l.src l.func l.irs r.irs
    rep = []
    for key in leftHash:
        sf = re.split(r':', key)
        assert len(sf) == 2

        l_irs  = leftHash[key][0]
        l_src  = sf[0]
        l_func = sf[1]
        l_mod  = leftHash[key][1]

        if key in rightHash:
            r_irs = rightHash[key][0]
        else:
            r_irs = 0

        rep.append( [l_src, l_func, l_irs, r_irs] )

    # sort array by left ir values
    rep.sort(key = getLeftIr)

    # print report as CSV table
    for fields in rep:
        l_src  = fields[0]
        l_func = fields[1]
        l_irs  = fields[2]
        r_irs  = fields[3]

        print( l_src + '\t' + l_func + '\t' + l_irs.__str__() + '\t' + r_irs.__str__() )


         














main()


#splitReportLine( str )

