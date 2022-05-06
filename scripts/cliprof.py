import fcntl
import sys
import termios
import re
from os.path import exists
import os
#import codecs
import time

def printUsage():
    print(sys.argv[0] + " -c command_file -p pid -f fifo_file -o (debug|report)")



def decodeEscaped(str):
     decoded_string = str.encode('latin-1','backslashreplace').decode('unicode_escape')
     return decoded_string


def readArguments():
    ARGS={}
    if len(sys.argv) == 9:
        argv = list(sys.argv)
        argv.pop(0)
        assert len(argv) == 8
        for i in range(4):
            if argv[0] == "-c":
                ARGS['file'] = argv[1]
            elif argv[0] == "-p":
                ARGS['pid'] = argv[1]
            elif argv[0] == "-f":
                ARGS['fifo'] = argv[1]
            elif argv[0] == "-o":
                ARGS['out'] = argv[1]
            else:
                printUsage()
                exit(1)
            
            argv.pop(0)
            argv.pop(0)
    else:
        printUsage()
        exit(1)

    # check arguments
    if not bool(re.match(r"^[0-9]+$", ARGS['pid'])):
        print("wrong syntax at '{}'".format(ARGS['pid']))
        printUsage()
        exit(2)

    if not exists(ARGS['file']):
        print("unable to locate file '{}'".format(ARGS['file']))
        printUsage()
        exit(2)

    if not exists(ARGS['fifo']):
        print("unable to locate fifo '{}'".format(ARGS['fifo']))
        printUsage()
        exit(2)

    if not (ARGS['out'] == 'debug' or ARGS['out'] == 'report'):
        print("wrong out format '{}'".format(ARGS['out']))
        printUsage()
        exit(2)


    return ARGS

# read with no trailing '\n' char
def readLines(fName):
    try:
        f = open(fName, 'r')
        fLines = f.readlines()
        for i in range(len(fLines)):
            fLines[i] = re.sub(r'\n$', "", fLines[i])
           
    except:
        printf("unable to open file '{}' for reading".format(fName))
        exit(3)
    return fLines

# out represents an output format:
# out in {'debug', 'report'}
def main():
    ARGS = readArguments()
    lines = readLines(ARGS['file'])

    out = ARGS['out']
    max_duration_time = 0
    total_duration_time = 0


    for i in range(len(lines)):
        lines[i] = decodeEscaped(lines[i])

    try:
        stdin = "/proc/{}/fd/0".format(ARGS['pid'])
        with open(stdin, 'w') as sin, open(ARGS['fifo'], 'r') as fifo:
            # try to empty FIFO pipe
            fifo.read()
           
            for iline in lines:
                # skip lines beginning with '#'
                if bool(re.match(r'^\s*#', iline)):
                    continue

                if out == 'debug':
                    print("----->send command: {}".format(iline.encode()))

                for char in iline:
                    fcntl.ioctl(sin, termios.TIOCSTI, char)

                # this is a start point waiting for CLI to respond
                start_time = time.clock_gettime_ns(time.CLOCK_MONOTONIC)

                # expect ending either '> ' or '> \7'
                oline = fifo.read()
                while len(oline) < 2 or not (oline[-2:] == ' \x07' or oline[-2:] == '> '):
                    oline = oline + fifo.read()

                # this is an end point waiting for CLI to repond
                finish_time = time.clock_gettime_ns(time.CLOCK_MONOTONIC)

                # convert nanoseconds to milliseconds
                duration_time = int((finish_time - start_time) / 1000000)

                if duration_time > max_duration_time:
                    max_duration_time = duration_time
                total_duration_time = total_duration_time + duration_time



                # remove \7 cursor char
                oline = re.sub("\x07", "", oline)


                if out == 'debug':
                    print("----->respond obtained: {}".format(oline.encode())) 

                if out == 'report':
                   print("{}\t{}\t{}".format(
                       iline.encode('latin-1', errors='backslashreplace'),
                       oline.encode('latin-1', errors='backslashreplace'),
                       duration_time))



    except Exception as error:
        print(str(error)) 

    # print time summary if 'report'
    if out == 'report':
        print("")
        print("max = {} ms, total = {} ms".format(max_duration_time, total_duration_time))




main()

#with open('/dev/pts/0', 'w') as fd:
#        fcntl.ioctl(fd, termios.TIOCSTI, "\t")
