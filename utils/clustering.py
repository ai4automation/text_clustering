import spacy
from nltk import ngrams
import math

def candidate_phrase(sentence):
    n = [4]
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

def document_phrase_frequency(phrase, documents):
    df = 0
    pf = 0
    for doc in documents:
        if len(doc.split()) > 0:
            if phrase in doc:
                df = df + 1
                pf = pf + (doc.count(phrase) / float(len(doc.split())))

    df = df / float(len(documents))
    return df, pf

def ranking(M, documents):
    ranking = {}
    for seq in M:
        df, pf = document_phrase_frequency(seq, documents)
        ranking[seq] = pf * (-math.log(1 - df))

    sequence_sorted = sorted(ranking, key=ranking.get, reverse=True)[:50]
    #final_phrases = filter(lambda x: [x for i in sequence_sorted if len(list(set(x.split(' ')) & set(i.split(' '))))>1 and x!=i], sequence_sorted)
    final_phrases = filter(lambda x: [x for i in sequence_sorted if x in i and x != i] == [], sequence_sorted)
    return final_phrases
