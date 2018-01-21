import argparse
from tokenizer import tokenize
from tokenizer import compute_word_frequencies

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
    args = parser.parse_args()
    filepath_1 = args.filepath1
    filepath_2 = args.filepath2
    tokens_1 = tokenize(filepath_1)
    tokens_2 = tokenize(filepath_2)
    word_frequencies_1 = compute_word_frequencies(tokens_1)
    word_frequencies_2 = compute_word_frequencies(tokens_2)

    count = count_common(word_frequencies_1, word_frequencies_2, True)
    print(count)

if __name__=='__main__':
    main()