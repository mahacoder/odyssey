import argparse
import re
from collections import defaultdict
from collections import Counter

separator = ' '

def print_sorted_order(frequency_map, **kwargs):
    freq_sort = [(v, k) for (k, v) in frequency_map.items()]
    freq_sort.sort(reverse=True)

    if 'output_file_name' in kwargs:
        with open(kwargs['output_file_name'], 'w+') as f:
            for (k,v) in freq_sort:
                f.write(str(k)+','+str(v)+'\n')
    else:
        for (k,v) in freq_sort:
            print(k, v)


def compute_word_frequencies(tokens):
    frequencies = Counter(tokens)
    return frequencies

def modify(word):
    to_check = ['"', "?", ".", ";", "'", ",", "!", "`", ":", "-", "#", "(", ")"]
    while len(word)>0 and word[-1] in to_check:
        word=word[:-1]
    while len(word)>0 and word[0] in to_check:
        word = word[1:]
    return word

def tokenize(text_file_path):
    tokens = []
    with open(text_file_path, encoding="utf-8") as file:
        try:
            for line in file:
                for word in line.split(separator):
                    word = re.sub('[^A-Za-z\d]+', '', word)
                    if len(word)!=0: tokens.append(str.lower(word))
        except Exception as e:
            raise Exception('Cannot read file. Caught exception')
    return tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path of the file to tokenize")
    args = parser.parse_args()
    filepath = args.filepath
    tokens = tokenize(filepath)
    print('Length of tokens =', len(tokens))
    word_frequencies = compute_word_frequencies(tokens)
    print_sorted_order(word_frequencies, output_file_name='output/regex _tokens.txt')
    print('Unique words =', len(word_frequencies))


if __name__=='__main__':
    main()