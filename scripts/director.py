import fcntl
import sys
import termios
import re
from os.path import exists
import os
import codecs

def printUsage():
    print(sys.argv[0].__str__() + " -c command_file -p pid")



def decodeEscaped(str):
     decoded_string = str.encode('latin-1','backslashreplace').decode('unicode_escape')
     return decoded_string


def readArguments():
    ARGS={}
    if len(sys.argv) == 5:
        argv = list(sys.argv)
        argv.pop(0)
        assert len(argv) == 4
        for i in range(2):
            if argv[0] == "-c":
                ARGS['file'] = argv[1]
            elif argv[0] == "-p":
                ARGS['pid'] = argv[1]
            else:
                printUIsage()
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


def main():
    ARGS = readArguments()
    lines = readLines(ARGS['file'])

    FIFO = "/home/ykuznetsov/klish-2.1.3/bin/.libs/fifo.file"

    for i in range(len(lines)):
        lines[i] = decodeEscaped(lines[i])

    try:
        stdin = "/proc/{}/fd/0".format(ARGS['pid'])
        with open(stdin, 'w') as sin, open(FIFO, 'r') as fifo:
            # try to empty FIFO pipe
            fifo.read()
           
            for line in lines:
                print("----->send command: {}".format(line.encode()))
                for char in line:
                    fcntl.ioctl(sin, termios.TIOCSTI, char)
                
                line = fifo.read()
                while len(line) == 0:
                    line = fifo.read()

                while line[-1] != '\x07':
                    tail = fifo.read()
                    line = line + tail
                print("----->respond obtained: {}".format(line.encode())) 


    except Exception as error:
        print(str(error)) 



main()

#with open('/dev/pts/0', 'w') as fd:
#        fcntl.ioctl(fd, termios.TIOCSTI, "\t")
