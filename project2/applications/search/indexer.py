import os
import sys
import pprint
sys.path.append(os.path.join(os.getcwd(), 'odyssey'))

from tokenizer import tokenize

class Indexer():

    def __init__(self):
        self.inverted_index_list = {}

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

    #custructing part (whole)
    def construct_index(self, directory_path):
        tokens_from_file = []
        for file_path in os.listdir(directory_path): 
             tokens_from_file = tokenize(os.path.join(directory_path, file_path))
             self.create_document_inverted_list(tokens_from_file, file_path)

#tf = count the number of positions> DONE
def term_frequency(self, term, document_name):
    return len(self.inverted_index_list[term][document_name])

#in the website, they use this function and so as lecture
def sublinear_term_frequency(self, term, document_name):
    return 1 + math.log(term_frequency(term, document_name))

#function for calculating idf
def inverse_document_frequencies(self, term):
    # pass directory name or make it global
    file_list = os.listdir("directory name")#calcuate N
    return math.log(len(file_list)/len(self.inverted_index_list[term]))

#calculate the tfidf
def tfidf(self, term, document_name):
    idf = self.inverse_document_frequencies(term)
    tf = self.sublinear_term_frequency(term, document_name)
    return tf * idf

if __name__=='__main__':
    cwd = os.getcwd()
    path_till_odyssey = cwd[:cwd.index('odyssey')+len('odyssey')]
    pages_dir_name = 'pages'
    print('path to pages: ', os.path.join(path_till_odyssey, pages_dir_name))
    indexer = Indexer()
    indexer.construct_index(os.path.join(path_till_odyssey, pages_dir_name))
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(indexer.inverted_index_list)