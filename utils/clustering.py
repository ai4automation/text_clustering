import spacy
from nltk import ngrams
import numpy as np
import math

def candidate_phrase(sentence):
    n = [3,4]
    phrases = []
    for i in n:
            n_grams = ngrams(sentence.split(),i)
            phrases.extend([ ' '.join(grams) for grams in n_grams])

    output_phrases = []
    nlp = spacy.load('en')
    for p in phrases:
        doc = nlp(p)
        #if 'datum request' in p:
        #    print(p, [token.pos_ for token in doc], len(list(doc.ents)), len(list(doc.noun_chunks)))
        if len(list(doc.ents)) != 0:
            output_phrases.append(p)
        elif len(list(doc.noun_chunks)) != 0:
            output_phrases.append(p)
        elif sum([token.pos_ == 'VERB' for token in doc]) > 0:
            output_phrases.append(p)
        else:
            pass

    return output_phrases
