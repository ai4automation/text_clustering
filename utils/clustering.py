import spacy
from nltk import ngrams
import math

'''def candidate_phrase(sentence):
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

    return output_phrases'''

def document_phrase_frequency(phrase, documents, mapping):
    df = 0
    pf = 0
    for doc in documents:
        if len(doc.split()) > 0:
            if phrase in mapping[doc]:
                df = df + 1
                pf = pf + (mapping[doc].count(phrase) / float(len(mapping[doc].split())))

    df = df / float(len(documents))
    return df, pf

def ranking(M, documents,mapping):
    ranking = {}
    for seq in M:
        df, pf = document_phrase_frequency(seq, documents, mapping)
        ranking[seq] = pf * (-math.log(1 - df))

    sequence_sorted = sorted(ranking, key=ranking.get, reverse=True)[:50]
    return sequence_sorted, ranking

def post_process(ranked_list, M, n=2):
	final_list = []
	for phrase in ranked_list:
		flag = 0
		for phrase_2 in final_list:
			intersect_phrase = list(set(phrase.split(' ')) & set(phrase_2.split(' ')))
			if len(intersect_phrase)==n:
				print(intersect_phrase)
				flag = 1
				break
		if flag==0:
			final_list.append(phrase)
	return final_list
