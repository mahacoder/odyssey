import argparse
import re
import codecs
import nltk
from collections import defaultdict
from collections import Counter

separator = ' '

def print_sorted_order(frequency, **kwargs):
    freq_sort = sorted(frequency.items(), key=lambda x:x[1], reverse=True)

    if 'output_file_name' in kwargs:
        with codecs.open(kwargs['output_file_name'], 'w+', 'utf-8') as f:
            for (k,v) in freq_sort:
                f.write(k+','+str(v)+'\n')
    else:
        for (k,v) in freq_sort:
            print(k, v)


def compute_word_frequencies(tokens):
    frequencies = Counter(tokens)
    return frequencies


def tokenize(text_file_path, use_nltk=False):
    tokens = []

    if use_nltk:
        file_content = codecs.open(text_file_path, 'r', 'utf-8').read()
        tokens = nltk.word_tokenize(file_content)
    else:
        with codecs.open(text_file_path, 'r', 'utf-8') as file:
            for line in file:
                for word in line.split(separator):
                    word = re.sub('[^A-Za-z\d]+', '', word)
                    if len(word)!=0: tokens.append(str.lower(word))
    return tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path of the file to tokenize")
    parser.add_argument("--output_file", help="path of the output file")
    args = parser.parse_args()
    filepath = args.filepath
    tokens = tokenize(filepath)
    word_frequencies = compute_word_frequencies(tokens)
    if args.output_file:
        print_sorted_order(word_frequencies, output_file_name=args.output_file)
    else:
        print_sorted_order(word_frequencies)


if __name__=='__main__':
    main()
