#! /bin/sh

python3 ExtractData.py --index arxiv_def --minfreq "$1" --maxfreq "$2" --numwords 210
python3 GeneratePrototypes.py --nclust 10
python3 MRKmeans.py --iter 8 -nmaps 4 --nreduces 4


