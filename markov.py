#  program to generate random pieces of text from two Wikipedia articles using a trigram Markov model

import re
from collections import defaultdict

# regex for tokenizing a piece of text. First attempts to match special contracted words with apostrophes such as don't, I'm, your's, I'd
# then attempts to matches all alphanumeric and underscores
# finally attempts to match STOP symbols
token = r"[A-Za-z]+'[smtld]|\w+|[.!?]"
STOP_SYMBOLS = ('.', '?', '!')
def build_trigram_index(text):
    """ Build and return a data structure that will allow us to look up bigram and trigram counts efficiently.

    The dictionary's keys will be bigrams, and the values will be lists with the first entry as the count of the bigram,
    and the second entry will be a dict with keys as last words of the trigram formed from the bigram.
    This will allow us to efficiently look up the most common trigram count relative to a bigram.
    """
    # initialize a list of words for the trigram with the START symbol *, which will allow us to generate text from a single seed word.
    trigram = ['*', '*', '*'] 
    ## trigram_counts = defaultdict(int)
    trigram_index = {}
    for t in re.finditer(token, text):
        w = t.group().lower()
        if t.group() in STOP_SYMBOLS:
            w = 'STOP'
            if trigram[2] == 'STOP':
                continue
        trigram[0] = trigram[1]
        trigram[1] = trigram[2]
        trigram[2] = w
        if trigram[0] == 'STOP':
            trigram[0] = '*'
        ##  trigram_counts[' '.join(trigram)] += 1

        # look up to see if we've already seen the bigram.
        # if not, add new entry to trigram_index with a count of 1.
        # if we have, add or increment the last word of the trigram by 1.
        bigram = ' '.join(trigram[:2]) 
        entry = trigram_index.get(bigram)
        if not entry:
            trigram_index[bigram] = [1, defaultdict(int)]
        else:
            trigram_index[bigram][0] += 1
        trigram_index[bigram][1][trigram[-1]] += 1
        ## trigram_counts[bigram].append(trigram[2])
        # if word is STOP, then consider as new starting point for a sentence

    return trigram_index 

def markov_generator(seed_bigram, trigram_index, n):
    s = seed_bigram
    bigram = seed_bigram.split()
    i = 0
    while i < n:
        # if first word is STOP, then add a period, and start sentence over
        if bigram[0] == 'STOP':
            bigram[0] = '*'
        i += 1
        entry = trigram_index[' '.join(bigram)]
        bigram_count = entry[0]
        next_words = entry[1]
        next_word = sorted([(count, word) for (word, count) in next_words.iteritems()], reverse=True)[0][1]
        if next_word == 'STOP':
            s += '. '
        else:
            s += ' ' + next_word
        bigram[0] = bigram[1]
        bigram[1] = next_word 
    return s

def main():
    with open('sherlock.txt') as f:
        text = f.read()
    with open('earnest.txt') as f:
        text += f.read()
    return build_trigram_index(text)


