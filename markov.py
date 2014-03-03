#  program to generate random pieces of text from two Wikipedia articles using a trigram Markov model

import re
token = r"[A-Za-z]+'[smtd]|\w+" 
# regex for tokenizing a piece of text. First attempts to match special contracted words with apostrophes such as don't, I'm, her's, I'd
# then attempts to matches all alphanumeric and underscores as other words

def word_tokenizer(text):
    for t in re.finditer(token, text):
        yield t.group().lower()


