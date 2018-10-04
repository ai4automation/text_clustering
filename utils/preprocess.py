import spacy
import re
from nltk import ngrams
from nltk.corpus import stopwords


def clean_html(text):
    html_remover = re.compile('<.*?>')
    text = re.sub(html_remover, ' ', text).replace('&nbsp;', ' ')
    text = text.replace('\n', '')
    text = text.replace('\t', '')
    text = text.replace(',', '.')
    text = text.replace(';', '.')
    text = text.replace('?', '? ')
    text = text.replace('!', '! ')
    text = text.replace('[', ' ')
    text = text.replace(']', ' ')
    text = text.replace('(', ' ')
    text = text.replace(')', ' ')
    text = text.replace('}', ' ')
    text = text.replace('{', ' ')
    text = text.replace("'m", ' am')
    return text


def clean_punctuation(text):
    text = text.replace(' -', '-')
    text = text.replace('- ', '-')
    text = text.replace(' /', '/')
    text = text.replace('/ ', '/')
    return text


def remove_unwanted_pos(text, nlp):
    stop_words = stopwords.words('english')
    doc = nlp(text)

    ENT_TYPES = ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
    POS_TAGS = ['INTJ', 'AUX', 'CCONJ', 'ADP', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X', 'MD']
    ALLOWED_PUNCTUATION = ['/', '-']

    output_sentences = []

    # re-tokenize for words with hyphen and forward-slash
    try:
        for token in doc:
            if token.lower_ in ALLOWED_PUNCTUATION:
                try:
                    token_index = token.i
                    start_offset = doc[token_index - 1].idx
                    end_offset = doc[token_index + 1].idx + doc[token_index + 1].__len__()
                    doc.merge(start_offset, end_offset)
                except IndexError:
                    pass
    except IndexError:
        pass

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

            if token.like_url:
                continue

            if token.like_email:
                continue

            if token.lower_ in stop_words:
                continue

            if any(char.isdigit() for char in token.lower_):
                continue

            # large noun phrases and named entity processing
            if len(token.text.split()) > 1:
                small_doc = nlp(token.text)
                start, end = 0, len(small_doc)

                # re-tokenize combining hyphens and forward slash
                try:
                    for small_token in small_doc:
                        if small_token.text in ALLOWED_PUNCTUATION:
                            try:
                                token_index = small_token.i
                                start_offset = small_doc[token_index - 1].idx
                                end_offset = small_doc[token_index + 1].idx + small_doc[token_index + 1].__len__()
                                small_doc.merge(start_offset, end_offset)
                            except IndexError:
                                continue
                except IndexError:
                    pass

                for i in range(len(small_doc)):
                    first_token = list(small_doc)[i]
                    if first_token.pos_ in POS_TAGS or first_token.is_stop or first_token.tag_ in POS_TAGS \
                            or first_token.is_punct:
                        start = i + 1
                    else:
                        break

                for j in range(len(small_doc) - 1, -1, -1):
                    last_token = list(small_doc)[j]
                    if last_token.pos_ in POS_TAGS or last_token.is_stop or last_token.tag_ in POS_TAGS \
                            or last_token.is_punct:
                        end = j - 1
                    else:
                        break

                small_docs_token_lemma = []

                for t in small_doc[start:end]:
                    if t.is_punct and t.text not in ALLOWED_PUNCTUATION:
                        continue
                    elif t.tag_ in POS_TAGS or t.pos_ in POS_TAGS:
                        continue
                    elif t.lower_ in stop_words:
                        continue
                    elif any(char.isdigit() for char in t.lower_):
                        continue
                    else:
                        small_docs_token_lemma.append(t)
                output_tokens.extend(small_docs_token_lemma)
            else:
                output_tokens.append(token)
        output_sentences.append(output_tokens)
    return output_sentences


def get_n_grams(list_of_texts, n=3):
    POS_TAGS = ['INTJ', 'AUX', 'CCONJ', 'ADP', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X', 'MD']

    nlp = spacy.load('en')

    list_of_texts = list(set(list_of_texts))
    raw_texts = list_of_texts
    list_of_texts = [clean_html(text) for text in list_of_texts]

    list_of_texts = [remove_unwanted_pos(text, nlp) for text in list_of_texts]

    # make mapping of raw text to processed text
    flatten_list_of_texts = []
    for text in list_of_texts:
        flatten_list_of_texts.append(' '.join(list(filter(lambda x: x not in ['', ' '],
                                                          [item.lower_.strip() for sublist in text for item in
                                                           sublist]))))
    raw_to_processed_text_mapping = {key: value for (key, value) in zip(raw_texts, flatten_list_of_texts)}

    # generate N-grams
    all_n_grams, sentence_n_grams = [], {}
    for text in list_of_texts:
        text_n_grams = []
        for sentence in text:
            new_sentence = list(filter(lambda x: len(x.lower_) > 1, sentence))
            n_grams = ngrams(new_sentence, n)
            text_n_grams.extend(n_grams)
        all_n_grams.append(text_n_grams)

    # filter N-grams
    output_phrases = []

    for text in all_n_grams:
        one_text_ngrams = []
        for one_ngram in text:
            if one_ngram[0].pos_ in POS_TAGS or one_ngram[0].tag_ in POS_TAGS:
                pass
            elif one_ngram[-1].pos_ in POS_TAGS or one_ngram[-1].tag_ in POS_TAGS:
                pass
            elif sum([len(token.text) == 0 for token in one_ngram]) > 0:
                pass
            elif sum([token.text == ' ' for token in one_ngram]) > 0:
                pass
            elif sum([len(token.text) == 0 for token in one_ngram]) > 0:
                pass
            elif len(' '.join([ng.lower_.strip() for ng in one_ngram]).strip().split()) != n:
                pass
            elif sum([token.pos_ == 'VERB' for token in one_ngram]) > 0:
                one_text_ngrams.append(' '.join([ng.lower_.strip() for ng in one_ngram]).strip())
            elif len(list(one_ngram[0].doc.ents)) > 0:
                one_text_ngrams.append(' '.join([ng.lower_.strip() for ng in one_ngram]).strip())
            elif len(list(one_ngram[0].doc.noun_chunks)) > 0:
                one_text_ngrams.append(' '.join([ng.lower_.strip() for ng in one_ngram]).strip())
            else:
                pass
        output_phrases.append(one_text_ngrams)

    # make text to N-gram mapping
    text_to_ngram = {text: ngrams_list for (text, ngrams_list) in
                     zip(raw_texts, output_phrases)}

    # make set of output phrases
    output_phrases = list(set([item for sublist in output_phrases for item in sublist]))

    return raw_to_processed_text_mapping, text_to_ngram, output_phrases


if __name__ == '__main__':
    import json

    obj = json.load(open('/Users/tanmayee/Downloads/test_4.json'))
    print(get_n_grams(obj[:3]))
