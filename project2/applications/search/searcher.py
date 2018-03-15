import os
import sys
import pprint
import indexer
import random
import json

sys.path.append(os.path.join(os.getcwd(), 'odyssey'))

from tokenizer import tokenize

def search_query(query):
    global path_till_odyssey
    ind = indexer.Indexer()
    ind.initialize_index(os.path.join(path_till_odyssey, pages_dir_name))
    inverted_index_list = ind.inverted_index_list
    score = 0
    results = {}
    for term in query:
        if term not in inverted_index_list:
            print("??")
            pass
        else:
            for doc in inverted_index_list[term]:
                if doc in results:
                    results[doc] += ind.tfidf(term, doc)
                else:
                    results[doc] = ind.tfidf(term, doc)
        '''If no search results, return random results
        Need to work on this more and try to find better results

        no_result_flag = True
        for key, value in results.items():
            if value!=0.0:
                no_result_flag = False

        if no_result_flag:
            results = {}
            for i in range(1):
                term = random.choice(inverted_index_list.keys())
                doc = random.choice(inverted_index_list[term].keys())
                results[doc] = 0
            return results
        '''
        return results

def top_num_results(frequency):
    freq_sort = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
    return freq_sort

def find_url(docs, num):
    with open('webpages_clean/bookkeeping.json', 'r') as fp:
        url_list = json.load(fp)
        print('File names...')
        '''for i in docs:
            doc_name = i[0]
            value = i[1]
            print(url_list[doc_name], value)'''
        for i in docs:
            doc_name = i[0]
            print(url_list[doc_name])

if __name__ == '__main__':
    cwd = os.getcwd()
    with open('doc_lengths.json', 'r') as fp:
        list1 = json.load(fp)

    path_till_odyssey = cwd[:cwd.index('odyssey')+len('odyssey')]
    pages_dir_name = 'webpages_clean'
    print("Please enter query:")
    query = raw_input().split()
    find_url(top_num_results(search_query(query)),5)
