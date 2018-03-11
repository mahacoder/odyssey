import os
import sys
import pprint
import pickle
import indexer

sys.path.append(os.path.join(os.getcwd(), 'odyssey'))

from tokenizer import tokenize

def search_query(query):
    ind = indexer.Indexer()
    ind.construct_index(os.path.join(path_till_odyssey, pages_dir_name))
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
        return results

def top_num_results(frequency, num = 3):
    freq_sort = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
    return freq_sort[:num]

if __name__ == '__main__':
    cwd = os.getcwd()
    path_till_odyssey = cwd[:cwd.index('odyssey')+len('odyssey')]
    pages_dir_name = 'pages'
    print("Please enter query:")
    query = raw_input().split()
    for i in top_num_results(search_query(query),3):
        print i[0]
