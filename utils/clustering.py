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


def ranking(M, documents, mapping):
    ranking = {}
    for seq in M:
        df, pf = document_phrase_frequency(seq, documents, mapping)
        ranking[seq] = pf * (-math.log(1 - df))

    sequence_sorted = sorted(ranking, key=ranking.get, reverse=True)[:50]
    return sequence_sorted, ranking


def longest_sub_phrase(phrase_1, phrase_2):
    phrase_1, phrase_2 = phrase_1.split(), phrase_2.split()
    assert len(phrase_1) == len(phrase_2)
    n = len(phrase_1)
    for sub_phrase in [phrase_1[i:i + (n - 1)] for i in range(0, 2)]:
        if sub_phrase in [phrase_2[i:i + (n - 1)] for i in range(0, 2)]:
            return ' '.join(sub_phrase)
    return None


def post_process(ranked_list, M, documents, mapping, n=3):
    final_list = []
    merge = {}
    for phrase in ranked_list:
        flag = 0
        for phrase_2 in final_list:
            intersect_phrase = longest_sub_phrase(phrase, phrase_2)
            if len(intersect_phrase) == n - 1:
                # print(intersect_phrase)
                if ' '.join(intersect_phrase) not in merge:
                    merge[' '.join(intersect_phrase)] = [phrase, phrase_2]
                else:
                    list_merge = merge[' '.join(intersect_phrase)]
                    list_merge.append(phrase)
                    list_merge.append(phrase_2)
                    merge[' '.join(intersect_phrase)] = list_merge
                flag = 1
                # break
        if flag == 0:
            final_list.append(phrase)
    print(merge)
    for phrase in merge.keys():
        score_children = []
        for children in merge[phrase]:
            score_children.append(M[children])
        df, pf = document_phrase_frequency(phrase, documents, mapping)
        score_parent = pf * (-math.log(1 - df))
        if score_parent > max(score_children):
            final_list.append(phrase)
            final_list = list(set(final_list) - set(merge[phrase]))
    return final_list
