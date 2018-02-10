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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wordmap1", help="path of the word map to compare")
    parser.add_argument("wordmap2", help="path of the word map to compare")
    parser.add_argument("--output_file", help="path of the output file")
    args = parser.parse_args()
    filepath_1 = args.wordmap1
    filepath_2 = args.wordmap2
    word_frequencies_1 = read_map(filepath_1)
    word_frequencies_2 = read_map(filepath_2)
    word_frequency = combine_frequency_map(word_frequencies_1, word_frequencies_2)
    if args.output_file:
        print_sorted_order(word_frequency, output_file_name=args.output_file)
    else:
        print_sorted_order(word_frequency)

if __name__=='__main__':
    main()