from __future__ import print_function
import json
import os
import sys
import time
import pprint
import pickle
import math
import nltk
from nltk.stem.porter import *
from tqdm import tqdm

sys.path.append(os.path.join(os.getcwd(), 'odyssey'))

from tokenizer import tokenize

class Indexer():

    def __init__(self):
        self.inverted_index_list = {}
        try:
            with open('index_tracker.p', 'r') as fp:
                self.inverted_index_tracker = pickle.load(fp)
        except:
            self.inverted_index_tracker = set()

    def add_to_index_tracker(self, processed_file):
        self.inverted_index_tracker.add(processed_file)

    #creating inverted index per term
    def create_inverted_index(self, term, document, position_list):
        #if term is new, then make a new document list
        if term not in self.inverted_index_list:
            document_list = {}
            document_list[document] = position_list
            self.inverted_index_list[term] = document_list
        #if term is existed, then append to a document list
        else:
            if document not in self.inverted_index_list[term]:
                self.inverted_index_list[term][document] = position_list

    #this function is converting all terms in the document into inverted index
    def create_document_inverted_list(self, tokens, document):
        for term in tokens:
            position_list = [idx for idx, val in enumerate(tokens) if term==val]
            self.create_inverted_index(term, document, position_list)

    def construct_index(self, directory_path):
        '''Constructs the inverted index'''

        tokens_from_file = []
        stemmer = PorterStemmer()
        counter=0
        for root, dirs, files in os.walk(directory_path):
            if len(dirs)!=0:
                continue # ignore the subdirectory without files
            dir_name = root[root.rindex('\\')+1:]
            print('{} folders processed till now'.format(counter))
            print('Process folder number {}'.format(dir_name))
            for file_ in tqdm(files):
                file_name = dir_name+'/'+file_
                if file_name in self.inverted_index_tracker:
                    continue
                file_path = os.path.join(root, file_)
                plurals = tokenize(file_path, use_nltk=True)
                tokens_from_file = [stemmer.stem(tokens) for tokens in plurals]
                self.create_document_inverted_list(tokens_from_file, file_path)
                self.add_to_index_tracker(file_name)
                # print('{} processed'.format(file_name))
                with open('index_tracker.p', 'wb') as fp:
                    pickle.dump(self.inverted_index_tracker, fp, protocol=pickle.HIGHEST_PROTOCOL)
            counter+=1

        # tokens_from_file = []
        # for file_path in os.listdir(directory_path):
        #      tokens_from_file = tokenize(os.path.join(directory_path, file_path))
        #      self.create_document_inverted_list(tokens_from_file, file_path)

    def initialize_index(self, directory_path):
        try:
            with open('inverted_index.p', 'rb') as fp:
                self.inverted_index_list = pickle.load(fp)
                return False #remove if not required
        except:
            self.construct_index(directory_path)
            return True #remove if not required
    #tf = count the number of positions
    def term_frequency(self, term, document_name):
        return len(self.inverted_index_list[term][document_name])

    #in the website, they use this function and so as lecture
    def sublinear_term_frequency(self, term, document_name):
        count =self.term_frequency(term, document_name)
        if count==0:
            return 0
        return 1 + math.log(count)

    #function for calculating idf
    def inverse_document_frequencies(self, term):
        # pass directory name or make it global
        cwd = os.getcwd()
        path_till_odyssey = cwd[:cwd.index('odyssey')+len('odyssey')]
        pages_dir_name = 'HTMLdocs'
        file_list = os.listdir(os.path.join(path_till_odyssey, pages_dir_name))
        if not self.inverted_index_list[term]:
            return 0
        return math.log(len(file_list)/len(self.inverted_index_list[term]))

    #calculate the tfidf
    def tfidf(self, term, document_name):
        idf = self.inverse_document_frequencies(term)
        tf = self.sublinear_term_frequency(term, document_name)
        return (tf*idf, tf, idf)

if __name__=='__main__':
    cwd = os.getcwd()
    path_till_odyssey = cwd[:cwd.index('odyssey')+len('odyssey')]
    pages_dir_name = 'webpages_clean'
    print('path to webpages: ', os.path.join(path_till_odyssey, pages_dir_name))
    indexer = Indexer()
    start = time.time()
    indexer.construct_index(os.path.join(path_till_odyssey, pages_dir_name))
    print('Constructed index in {}'.format(time.time()-start))
    with open('inverted_index.json', 'w') as fp:
        json.dump(indexer.inverted_index_list, fp)

    with open('inverted_index.p', 'wb') as fp:
        pickle.dump(indexer.inverted_index_list, fp, protocol=pickle.HIGHEST_PROTOCOL)
