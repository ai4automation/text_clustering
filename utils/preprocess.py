import spacy
import re
from nltk import ngrams


def clean_html(text):
    html_remover = re.compile('<.*?>')
    text = re.sub(html_remover, ' ', text).replace('&nbsp;', ' ')
    return text


def clean_punctuation(text):
    text = text.replace(' - ', '-')
    text = text.replace(' / ', '/')
    return text


def remove_unwanted_pos(text, nlp):
    doc = nlp(text)

    ENT_TYPES = ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
    POS_TAGS = ['INTJ', 'AUX', 'CCONJ', 'ADP', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
    ALLOWED_PUNCTUATION = ['/', '-']

    output_sentences = []

    for named_entity in list(doc.ents):
        named_entity.merge(tag=named_entity.root.tag_, lemma=named_entity.root.lemma_,
                           ent_type=named_entity.root.ent_type_)

    for noun_phrase in list(doc.noun_chunks):
        noun_phrase.merge(tag=noun_phrase.root.tag_, lemma=noun_phrase.root.lemma_, ent_type=noun_phrase.root.ent_type_)

    for sentence in doc.sents:
        output_tokens = []
        for token in sentence:
            if token.is_stop and token.text not in ALLOWED_PUNCTUATION:
                continue

            if token.is_punct and token.text not in ALLOWED_PUNCTUATION:
                continue

            if token.ent_type_ in ENT_TYPES:
                continue

            if token.tag_ in POS_TAGS or token.pos_ in POS_TAGS:
                continue

            # large noun phrases and named entity processing
            if len(token.text.split()) > 1:
                small_doc = nlp(token.text)
                start, end = 0, len(small_doc)

                for i in range(len(small_doc)):
                    first_token = list(small_doc)[i]
                    if first_token.pos_ in POS_TAGS or first_token.is_stop or first_token.tag_ in POS_TAGS \
                            or first_token.is_punct:
                        start = i+1
                    else:
                        break

                for j in range(len(small_doc)-1, -1, -1):
                    last_token = list(small_doc)[j]
                    if last_token.pos_ in POS_TAGS or last_token.is_stop or last_token.tag_ in POS_TAGS \
                            or last_token.is_punct:
                        end = j-1
                    else:
                        break

                small_docs_token_lemma = []

                for t in small_doc[start:end]:
                    if t.is_punct and t.text not in ALLOWED_PUNCTUATION:
                        continue
                    else:
                        small_docs_token_lemma.append(t)
                output_tokens.extend(small_docs_token_lemma)
            else:
                output_tokens.append(token)
        output_sentences.append(output_tokens)

    return output_sentences


def get_n_grams(list_of_texts, n=3):
    POS_TAGS = ['INTJ', 'AUX', 'CCONJ', 'ADP', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']

    nlp = spacy.load('en')

    list_of_texts = list(set(list_of_texts))
    list_of_texts = [clean_html(text) for text in list_of_texts]

    list_of_texts = [remove_unwanted_pos(text, nlp) for text in list_of_texts]

    all_n_grams = []
    for text in list_of_texts:
        text_n_grams = []
        for sentence in text:
            n_grams = ngrams(sentence, n)
            text_n_grams.extend(n_grams)
        all_n_grams.append(text_n_grams)

    output_phrases = []

    for text in all_n_grams:
        one_text_ngrams = []
        for one_ngram in text:
            if one_ngram[0].pos_ in POS_TAGS or one_ngram[0].tag_ in POS_TAGS:
                pass
            elif one_ngram[-1].pos_ in POS_TAGS or one_ngram[-1].tag_ in POS_TAGS:
                pass
            elif sum([token.pos_ == 'VERB' for token in one_ngram]) > 0:
                one_text_ngrams.append(' '.join([ng.lemma_ for ng in one_ngram]))
            elif len(list(one_ngram[0].doc.ents)) > 0:
                one_text_ngrams.append(' '.join([ng.lemma_ for ng in one_ngram]))
            elif len(list(one_ngram[0].doc.noun_chunks)) > 0:
                one_text_ngrams.append(' '.join([ng.lemma_ for ng in one_ngram]))
            else:
                pass
        output_phrases.append(one_text_ngrams)

    return output_phrases
