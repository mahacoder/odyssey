import argparse
from collections import defaultdict
from tokenizer import tokenize
from tokenizer import compute_word_frequencies
from tokenizer import print_sorted_order

def combine_frequency_map(frequency_map1, frequency_map2):
    map = defaultdict(int)
    for k, v in frequency_map1.items():
        map[k] = v
    for k, v in frequency_map2.items():
        if k in map: map[k]+=v
        else: map[k]=v
    return map

def read_map(filepath):
    map = defaultdict(int)
    with open(filepath) as f:
        for line in f:
            k, v = line.split(',')
            k, v = k.strip(), int(v.strip())
            if k in map: map[k]+=v
            else: map[k]=v
    return map

def count_common(frequency1, frequency2, print_common_keys=False):
    counter = 0
    for k, v in frequency1.items():
        if k in frequency2:
            counter+=1
            if print_common_keys: print(k, end=',')
    if print_common_keys: print()
    return counter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath1", help="path of the file to compare")
    parser.add_argument("filepath2", help="path of the file to compare")
    parser.add_argument("is_map", help="True if the files are frequency maps")
    args = parser.parse_args()
    filepath_1 = args.filepath1
    filepath_2 = args.filepath2
    is_map = args.is_map
    if is_map=='True' or is_map=='true':
        word_frequencies_1 = read_map(filepath_1)
        word_frequencies_2 = read_map(filepath_2)
        word_frequency = combine_frequency_map(word_frequencies_1, word_frequencies_2)
        print_sorted_order(word_frequency)
    else:
        tokens_1 = tokenize(filepath_1)
        tokens_2 = tokenize(filepath_2)
        word_frequencies_1 = compute_word_frequencies(tokens_1)
        word_frequencies_2 = compute_word_frequencies(tokens_2)
        count = count_common(word_frequencies_1, word_frequencies_2, True)
        print(count)

if __name__=='__main__':
    main()