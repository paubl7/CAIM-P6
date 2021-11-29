"""
.. module:: ProcessResults

ProcessPrototype
******

:Description: ProcessResults

    Prints the results of a clustering,basically the prototypes, selecting the --attr
    tokens with the highest probability

    It assumes that the results are written in a file with the adequate format

:Authors:
    bejar

:Version: 

:Date:  14/07/2017
"""


import argparse

__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes-final.txt', help='prototype file')
    parser.add_argument('--natt', default=5, type=int, help='Number of attributes to show')
    args = parser.parse_args()

    f = open(args.prot, 'r')

    for line in f:
        cl, attr = line.split(':')
        print(cl)
        latt = sorted([(float(at.split('+')[1]), at.split('+')[0]) for at in attr.split()], reverse=True)
        print(latt[:args.natt])

