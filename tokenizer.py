import argparse
from collections import defaultdict

separator = ' '

def compute_word_frequencies(tokens):
    frequencies = defaultdict(int)
    for token in tokens:
        frequencies[str.lower(token)]+=1

    freq_sort = [(v, k) for (k, v) in frequencies.items()]
    freq_sort.sort(reverse=True)
    # print frequencies
    for (k,v) in freq_sort:
        print(k, v)

def tokenize(text_file_path):
    tokens = []
    with open(text_file_path) as file:
        for line in file:
            words = line.split(separator)
            tokens.extend(words)
    return tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path of the file to tokenize")
    args = parser.parse_args()
    filepath = args.filepath
    tokens = tokenize(filepath)
    word_frequencies = compute_word_frequencies(tokens)
    print(word_frequencies)


if __name__=='__main__':
    main()
