import spacy
#from nltk import ngrams
import numpy as np
import math
#from sklearn.metrics.pairwise import cosine_similarity

def pre_process(text):
    '''
    Pre-process text according to Key2Vec paper
    :param text: string object to pre-process
    :return: list of tokens in input text
    '''
    ENT_TYPES = ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
    POS_TAGS = ['INTJ', 'AUX', 'CCONJ', 'ADP', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'PUNCT', 'SYM', 'X']

    output_tokens = []
    nlp = spacy.load('en')
    doc = nlp(text)

    for named_entity in list(doc.ents):
        named_entity.merge(tag=named_entity.root.tag_, lemma=named_entity.root.lemma_,
                           ent_type=named_entity.root.ent_type_)

    for noun_phrase in list(doc.noun_chunks):
        noun_phrase.merge(tag=noun_phrase.root.tag_, lemma=noun_phrase.root.lemma_, ent_type=noun_phrase.root.ent_type_)

    for sentence in doc.sents:
        for token in sentence:
            if token.is_stop:
                continue

            if token.is_punct:
                continue

            if token.ent_type_ in ENT_TYPES:
                continue

            if token.tag_ in POS_TAGS or token.pos_ in POS_TAGS:
                continue

            # large noun phrases and named entity processing
            if len(token.text.split()) > 1:
                small_doc = nlp(token.text)
                start, end = 0, len(small_doc)
                first_token, last_token = list(small_doc)[0], list(small_doc)[-1]
                if first_token.pos_ in POS_TAGS or first_token.is_stop or first_token.tag_ in POS_TAGS \
                        or first_token.is_punct:
                    start = 1
                if last_token.pos_ in POS_TAGS or last_token.is_stop or last_token.tag_ in POS_TAGS \
                        or last_token.is_punct:
                    end = -1
                small_docs_token_lemma = []
                for t in small_doc[start:end]:
                    if not t.is_punct:
                        small_docs_token_lemma.append(t.text)
                output_tokens.append(' '.join(small_docs_token_lemma))
            else:
                output_tokens.append(token.lemma_)

    return ' '.join(output_tokens)

'''def candidate_phrase(sentence):
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


def inclination_factor(em_source, em_dest, source, destination):
    ifac = 0.0
    ling_fac = 0.0
    sem_fac = 0.0
    #tf_em_dest = embed([destination])
    #tf_em_source = embed([source])
    #em_dest = session.run(tf_em_dest)
    #em_source = session.run(tf_em_source)
    sem_fac = (1-(np.arccos(cosine_similarity(em_source, em_dest)[0,0])/np.pi))
    char_trigram_source = [ ''.join(grams) for grams in ngrams(source,3)]
    char_trigram_dest = [ ''.join(grams) for grams in ngrams(destination,3)]
   
    ling_fac = len(list(set(char_trigram_source)&set(char_trigram_dest)))/min(len(char_trigram_source),len(char_trigram_dest))
    ifac = sem_fac * ling_fac
    print(source,",", destination, sem_fac, ling_fac)
    return ifac


def final_score(phrase, ifac, docs):
    df = 0
    pf = 0
    for doc in docs:
            if doc.split(' ')>1 and phrase in doc:
                    df = df + 1
                    pf = pf + (doc.count(phrase)/float(len(doc.split(' '))))
    df= df /float(len(docs))
    return ifac * pf * (-math.log(1-df))
'''

'''if __name__ == '__main__':
    embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder/1")
    session = tf.Session()
    session.run([tf.global_variables_initializer(), tf.tables_initializer()])
    #f = open('../data/BPI2016_Questions_Correspondence.txt', 'r')
    comments = f.readlines()
    candidate_phrases = []
    print(len(list(set(comments))))
    for comment in list(set(comments)):
        candidate_phrases.extend(candidate_phrase(pre_process(comment.lower().strip())))
    print(list(set(candidate_phrases)))
    candidate_set = list(set(candidate_phrases))
    ranking = {}
    n = len(list(set(comments)))
    for phrase in candidate_set:
        ifac = 0.0
        for comment in list(set(comments)):
            ifac += inclination_factor(phrase, pre_process(comment.lower().strip()),embed, session)
        ifac = ifac/float(n)
        ranking[phrase] = final_score(phrase, ifac, comments)
    print(ranking)
    key_phrases = sorted(ranking, key=ranking.get, reverse=True)
    print(key_phrases)
'''
