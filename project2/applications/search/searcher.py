import os
import sys
import pprint
import pickle
import indexer
import random

sys.path.append(os.path.join(os.getcwd(), 'odyssey'))

from tokenizer import tokenize

def search_query(query):
    ind = indexer.Indexer()
    ind.initialize_index(os.path.join(path_till_odyssey, pages_dir_name))
    inverted_index_list = ind.inverted_index_list
    score = 0
    results = {}
    for term in query:
        if term not in inverted_index_list:
            pass
        else:
            for doc in inverted_index_list[term]:
                if doc in results:
                    results[doc] += ind.tfidf(term, doc)
                else:
                    results[doc] = ind.tfidf(term, doc)
        '''If no search results, return random results
        Need to work on this more and try to find better results
        '''
        if not results:
            for i in range(10):
                term = random.choice(inverted_index_list.keys())
                doc = random.choice(inverted_index_list[term].keys())
                results[doc] = 0
        return results

def top_num_results(frequency, num):
    freq_sort = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
    return freq_sort[:num]

def find_url(docs):
    with open('doc_url_map.p', 'r') as fp:
        url_list = pickle.load(fp)
        for i in docs:
            print(url_list[i])

if __name__ == '__main__':
    cwd = os.getcwd()
    path_till_odyssey = cwd[:cwd.index('odyssey')+len('odyssey')]
    pages_dir_name = 'pages'
    print("Please enter query:")
    query = raw_input().split()
    find_url(top_num_results(search_query(query), 5))
