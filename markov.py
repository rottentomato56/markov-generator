"""  
Generate random pieces of text from two txt files using a trigram Markov model 

To run, call from command line: python markov.py text1 text2 n

text1, text2 = 2 different text files. The longer the better, as Markov models perform better with more training data.

n = maximum number of sentences returned.

Inspired by http://kingjamesprogramming.tumblr.com/
"""

import re
import random
import sys
from collections import defaultdict

# regex for tokenizing a piece of text. First attempts to match special contracted words with apostrophes such as don't, I'm, your's, I'd, I'll
# then attempts to matches all alphanumeric and underscores
# finally attempts to match STOP symbols

token = r"[A-Za-z]+'[smtld]l*|\w+|[.!?]"
STOP_SYMBOLS = ['.', '?', '!']
def build_trigram_index(text):
    """ Build and return a data structure that will allow us to look up bigram and trigram counts efficiently.

    Each entry in the dictionar will have a bigram as a key, and the value will be a list with the first entry as the count of the bigram,
    and the second entry will be a dict with keys as last words of the trigram formed from the bigram.
    This will allow us to efficiently look up the most common trigram count relative to a bigram.
    """
    
    # initialize a list of words for the trigram with the START symbol *, which will allow us to generate text from a bigram of the form '* word'
    trigram = ['*', '*', '*']
    
    # keep a set of bigrams that start sentences. Anytime we see a bigram of the form '* word', we add it to this set. This will allow us to generate random seeds for sentences.
    sentence_starters = []
    
    trigram_index = {}
    for t in re.finditer(token, text):
        w = t.group().lower()
        if w in STOP_SYMBOLS:
            w = 'STOP'
            # if the next word is STOP while the last word of the trigram is STOP, we skip it to avoid sequences of STOPs
            if trigram[2] == 'STOP':
                continue
        trigram[0] = trigram[1]
        trigram[1] = trigram[2]
        trigram[2] = w
        if trigram[0] == 'STOP':
            trigram[0] = '*'

        # look up to see if we've already seen the bigram.
        # if not, add new entry to trigram_index with a count of 1.
        # if we have alreayd seen it, add or increment the last word of the trigram by 1. 
        
        bigram = ' '.join(trigram[:2]) 
        entry = trigram_index.get(bigram)
        if not entry:
            trigram_index[bigram] = [1, defaultdict(int)]
        else:
            trigram_index[bigram][0] += 1
        trigram_index[bigram][1][trigram[-1]] += 1
        bigram_split = bigram.split()
        
        # only if the bigram begins with a START symbol and doesn't end with another START or STOP symbol, add it to the set of sentence starters
        if bigram_split[0] == '*' and bigram_split[1] not in ['*'] + STOP_SYMBOLS:
          sentence_starters.append(bigram_split)
    return trigram_index, sentence_starters

def markov_generator(trigram_index, sentence_starters,  n):
    # keep a memory of which trigrams have already been seen, since revisiting a trigram will cause an endless loop in the Markov chain. If a trigram has already been seen, choose the next most likely word to form a trigram.
    trigrams_used = {}
    paragraph = ''
    bigram = sentence_starters[random.randint(0, len(sentence_starters))]
    sentence = bigram[1]
    i = 0
    while i < n:
        # if bigram begins with STOP, then the chain has reached the beginning of a new sentence. Since we store sentence starters in the form of '* word', we change the first term of the bigram to a START symbol.
        if bigram[0] == 'STOP':
            bigram[0] = '*'
        entry = trigram_index[' '.join(bigram)]
        bigram_count = entry[0]
        possible_nextwords = entry[1]
        
        # sort the set of possible next words
        sorted_nextwords = sorted([(count, word) for (word, count) in possible_nextwords.iteritems()], reverse=True)
        next_word = None
        for next_wordpair in sorted_nextwords:
          trigram = bigram + [next_wordpair[1]]
          if ' '.join(trigram) not in trigrams_used:
            next_word = next_wordpair[1]
  
        # the chain terminates if we no longer have any possible trigrams to use   
        if not next_word:
          return paragraph
        if next_word == 'STOP':
            # if we reach the end of a sentence, add it to the paragraph, and start over.
            # biased to output longer sentences
            if len(sentence.split()) > 2:
              paragraph += sentence + '.'
              i += 1
            sentence = ''
        else:
            sentence += ' ' + next_word
        trigrams_used[' '.join(trigram)] = 1 # add the trigram to the set of already seen trigrams
        bigram[0] = bigram[1]
        bigram[1] = next_word
    return paragraph.strip()

def run(text1, text2, n):
    """ Main calling function that returns a block of text.
    
    text1, text2 = textfiles to train the Markov model
    n = maximum number of sentences to generate and output
    """
    
    with open(text1) as f:
        text = f.read()
    with open(text2) as f:
        text += f.read()
    trigram_index, sentence_starters = build_trigram_index(text)
    p = markov_generator(trigram_index, sentence_starters, n)
    return p


if __name__ == '__main__':
    if len(sys.argv) != 4:
      print 'Error: Incorrect arguments. To run, call:\npython markov.py text1 text2 max_sentences_returned'
      sys.exit()
    text1 = sys.argv[1] 
    text2 = sys.argv[2]
    try:
      n = int(sys.argv[3])
    except:
      print 'Not a number. Please try again'
      sys.exit()
    print run(text1, text2, n)

