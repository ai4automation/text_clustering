import spacy
from spacy_cld import LanguageDetector
import re
import json
from tqdm import tqdm
import traceback
from talon.signature.bruteforce import extract_signature
from langdetect import detect
from utils.regex_filters import regex_filters


def remove_regex(text, regex_list):
    for pattern in regex_list:
        pattern = pattern.replace('?', '\?')
        pattern = pattern.replace('[', '\[')
        pattern = pattern.replace(']', '\]')
        text = re.sub(pattern, """""", text, flags=re.I | re.S)
    text = re.sub("\[(.*)\]", """""", text, flags=re.I | re.S)
    text = re.sub("\*\*\*\*(.*)", """""", text, flags=re.I | re.S)
    return text


def remove_text(text, stopword_list):
    for word in stopword_list:
        text = re.sub(word, "", text, flags=re.I)
    return text


def spacy_pipeline(text, nlp):
    ENTITY_TYPES = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'LANGUAGE']
    OTHER_WORDS = ["hi", "hello", "hey"]

    english_sentences = []
    doc = nlp(text)
    for sentence in doc.sents:
        all_languages = sentence._.languages
        try:
            all_languages.append(detect(sentence.text))
        except:
            pass

        if len(all_languages) == 0 or 'en' in all_languages:
            english_sentences.append(sentence)

    filtered_tokens = []
    for sentence in english_sentences:
        for token in sentence:
            if token.ent_type_ in ENTITY_TYPES:
                continue
            if token.lemma_ in OTHER_WORDS:
                continue
            filtered_tokens.append(token)

    return ''.join([token.text_with_ws for token in filtered_tokens])


def email_pre_process(text, nlp, filters):
    text, _ = extract_signature(text)
    text = remove_regex(text, filters['regex'])
    text = remove_text(text, filters['text'])
    text = spacy_pipeline(text, nlp)

    return text.strip()


if __name__ == '__main__':
    with open('/Users/tanmayee/Downloads/BlueWorks_description.txt', encoding='utf-8') as f:
        lines = f.readlines()

    nlp = spacy.load('en')
    language_detector = LanguageDetector()
    nlp.add_pipe(language_detector)

    output, count = [], 0
    for line in tqdm(lines):
        try:
            output.append(email_pre_process(line, nlp, regex_filters))
        except:
            count += 1
            output.append(traceback.format_exc(limit=1))

    print('%f lines skipped, %d lines skipped' % (count / len(lines), count))
    json.dump(output, open('filtered_output.json', 'w'), indent=1)
