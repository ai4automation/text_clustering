import spacy
import re


def clean_html(text):
    html_remover = re.compile('<.*?>')
    text = re.sub(html_remover, ' ', text).replace('&nbsp;', ' ')
    return text


def pre_process(text):
    """
    Pre-process text according to Key2Vec paper
    :param text: string object to pre-process
    :return: list of preprocessed sentences
    """
    text = clean_html(text)

    ENT_TYPES = ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
    POS_TAGS = ['INTJ', 'AUX', 'CCONJ', 'ADP', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ', 'SYM', 'X']
    ALLOWED_PUNCTUATION = ['/', '-']

    output_sentences = []
    nlp = spacy.load('en')
    doc = nlp(text)

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
        output_sentences.append(output_tokens)

    output_sentences = [' '.join(sentence_tokens) for sentence_tokens in output_sentences]
    return output_sentences
