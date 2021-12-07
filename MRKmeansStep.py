"""
.. module:: MRKmeansDef

MRKmeansDef
*************

:Description: MRKmeansDef

    

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 7:42 

"""

from mrjob.job import MRJob
from mrjob.step import MRStep
import numpy as np
from np.ndarray import flatten

__author__ = 'bejar'

def unpack_prot(prot,total_count):
    words = []
    for word,prob in prot:
        w_occurences = prob*total_count
        words.append(np.repeat(word,w_occurences))
    unpacked = list(flatten(np.array(words)))
    return unpacked

def intersection(lst1, lst2):
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3
    
class MRKmeansStep(MRJob):
    prototypes = {}


    def jaccard(prot, doc):
        """
        Compute here the Jaccard similarity between  a prototype and a document
        prot should be a list of pairs (word, probability)
        doc should be a list of words
        Words must be alphabeticaly ordered
        The result should be always a value in the range [0,1]
        """
        prot_doc = unpack_prot(prot,len(doc))
        jaccard_similarity = len(intersection(prot_doc,doc))/len(prot+doc)
        return jaccard_similarity

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files

        :return:
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

    def load_data(self):
        """
        Loads the current cluster prototypes

        :return:
        """
        f = open(self.options.prot, 'r')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

    def assign_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document

        Words should be sorted alphabetically in the prototypes and the documents

        This function has to return at list of pairs (prototype_id, document words)

        You can add also more elements to the value element, for example the document_id
        """

        # Each line is a string docid:wor1 word2 ... wordn
        doc, words = line.split(':')
        lwords = words.split()

        minimum_distance = -1 
        assigned_prototype= ""
        for prot in self.prototypes:
            distance = self.jaccard(self.prototypes[prot], lwords)
            if (distance < minimum_distance or minimum_distance==-1):
                assigned_prototype = prot
                minimum_distance= distance
            
        # Return pair key, value
        yield assigned_prototype, (doc, lwords)

    def aggregate_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word

        :param key:
        :param values:
        :return:
        """

        new_prototype={}
        new_prototype_documents=[]
        n_documents=0
        for document in values:
            new_prototype_documents.append(document[0])
            for word in document[1]:
                if word in new_prototype:
                    new_prototype[word] += 1
                else:
                    new_prototype[word] = 1
            
            n_documents += 1

        returnPrototype = []
        for word in new_prototype:
            returnPrototype.append((word,new_prototype[word]/float(n_documents)))
    
        yield key, (sorted(new_prototype_documents),sorted(returnPrototype, key=lambda x: x[0]))
    
    
    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)
            ]


if __name__ == '__main__':
    MRKmeansStep.run()