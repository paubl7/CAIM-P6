"""
.. module:: ExtractData

ExtractData
*************

:Description: ExtractData

    Generates vector data representation with the most frequent words

:Authors: bejar
    

:Version: 

:Created on: 12/07/2017 8:20 

"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError

import argparse

__author__ = 'bejar'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--minfreq', default=0.0, type=float, required=False, help='Minimum word frequency')
    parser.add_argument('--maxfreq', default=1.0, type=float, required=False, help='Maximum word frequency')
    parser.add_argument('--numwords', default=None, type=int, required=False, help='Number of words')

    args = parser.parse_args()

    index = args.index
    minfreq = args.minfreq
    maxfreq = args.maxfreq
    numwords = args.numwords

    try:
        client = Elasticsearch(timeout=1000)
        voc = {}  # global vocabulary frequency
        docterms = {}  # document vocabulary
        print('Querying all documents ...')
        sc = scan(client, index=index, query={"query": {"match_all": {}}})
        print('Generating vocabulary frequencies ...')
        for s in sc:
            docpath = s['_source']['path']
            docterms[docpath] = set()  # use a set for efficient operations
            tv = client.termvectors(index=index, doc_type='document', id=s['_id'], fields=['text'])
            if 'text' in tv['term_vectors']:
                for t in tv['term_vectors']['text']['terms']:
                    docterms[docpath].add(t)
                    if t in voc:
                        voc[t] += 1
                    else:
                        voc[t] = 1
        lwords = []

        # Compute overall words relative frequency
        fmax = 0
        for v in voc:
            if voc[v] > fmax:
                fmax = voc[v]
            lwords.append((voc[v], v))

        lwords = sorted([(f / fmax, v) for f, v in lwords], reverse=True)

        lwords = [v for f, v in lwords if minfreq <= f <= maxfreq]

        if numwords and len(lwords) > numwords:
            lwords = set(lwords[:numwords])

        print('Computing binary term vectors ...')
        for doc in docterms:
            docterms[doc] = docterms[doc].intersection(lwords)

        print('Saving data ...')
        f = open('vocabulary.txt', 'w')
        for p in sorted(lwords):
            f.write(p.encode('ascii', 'replace').decode() + ' ' + str(voc[p]) + '\n')
        f.flush()
        f.close()

        f = open('documents.txt', 'w')
        for doc in docterms:
            docname = doc.split('/')
            docname = docname[-2] + '/' + docname[-1]
            docvec = ''
            for v in sorted(list(lwords)):
                docvec += (' ' + v) if v in docterms[doc] else ''
            if docvec:  # writes the document if there are words from the vocabulary
                f.write(docname + ':' + docvec.encode('ascii', 'replace').decode() + '\n')
        f.flush()
        f.close()

    except NotFoundError:
        print('Index %s does not exists' % index)
