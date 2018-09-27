import math
import json
from utils.preprocess import get_n_grams


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
    ranking_ = {}
    for seq in M:
        df, pf = document_phrase_frequency(seq, documents, mapping)
        ranking_[seq] = pf * (-math.log(1 - df))

    sequence_sorted = sorted(ranking_, key=ranking_.get, reverse=True)[:50]
    return sequence_sorted, ranking_


def longest_sub_phrase(phrase_1, phrase_2):
    phrase_1, phrase_2 = phrase_1.split(), phrase_2.split()
    assert len(phrase_1) == len(phrase_2)
    n = len(phrase_1)
    for sub_phrase in [phrase_1[i:i + (n - 1)] for i in range(0, 2)]:
        if sub_phrase in [phrase_2[i:i + (n - 1)] for i in range(0, 2)]:
            return ' '.join(sub_phrase)
    return ''


def post_process(ranked_list, M, documents, mapping, n=3):
    final_list = []
    merge = {}
    for phrase in ranked_list:
        flag = 0
        for phrase_2 in final_list:
            intersect_phrase = longest_sub_phrase(phrase, phrase_2)
            if len(intersect_phrase.split(' ')) == n - 1:
                # print(intersect_phrase)
                try:
                    list_merge = merge[intersect_phrase]
                    list_merge.append(phrase)
                    list_merge.append(phrase_2)
                    merge[intersect_phrase] = list_merge
                except KeyError:
                    merge[intersect_phrase] = [phrase, phrase_2]
                flag = 1
                # break
        if flag == 0:
            final_list.append(phrase)

    for phrase in merge.keys():
        df, pf = document_phrase_frequency(phrase, documents, mapping)
        score_parent = pf * (-math.log(1 - df))

        score_children = [M[children] for children in merge[phrase]]

        if score_parent > max(score_children):
            final_list.append(phrase)
            final_list = list(set(final_list) - set(merge[phrase]))
    return final_list


def filter_unwanted(candidates):
    unwanted = ["thank", "ibm", "please", "apologize", "dear", "sincerely", "helpdesk", "better",
                "help-desk", "telephone", "regards", "regret", "gmail", "yahoo", "hotmail",
                "center", "exit", "time", "access", "administrator", "support", "assist", "skills",
                "proveitsupport", "contact"]

    filtered = filter(lambda phrase_: not any(n in phrase_ for n in unwanted), candidates)
    filtered = list(filtered)

    return filtered


def find_labels(byte_stream, n=3, coverage=True):
    cluster = {}
    comments = json.loads(byte_stream)
    comments = list(set(comments))
    print("number of comments (unique): ", len(comments))
    mapping_preprocess, mapping_ngrams, candidates = get_n_grams(comments, n)

    ranked_phrases, score_dict = ranking(filter_unwanted(list(set(candidates))), comments, mapping_preprocess)

    final_list = post_process(ranked_phrases, score_dict, comments, mapping_preprocess)
    print("ranked list: ", final_list)
    if coverage:
        lookup_comments = [k for k in comments if len(list(set(mapping_ngrams[k]) & set(final_list))) == 0]
        for comm in lookup_comments:
            candidates_lookup = mapping_ngrams[comm]
            if len(candidates_lookup) > 0:
                ranked_lookup, score_lookup = ranking(filter_unwanted(list(set(candidates_lookup))), comments,
                                                      mapping_preprocess)
                if len(ranked_lookup) > 0:
                    final_list.append(ranked_lookup[0])
    final_list = list(set(final_list))

    for i in range(0, len(comments)):
        flag = 0
        for phrase in final_list:
            if phrase in mapping_preprocess[comments[i]]:
                flag = 1
                try:
                    list_comm = cluster[phrase]
                    list_comm.append(comments[i])
                    list_comm = list(set(list_comm))
                    cluster[phrase] = list_comm
                except KeyError:
                    cluster[phrase] = [comments[i]]

        if flag == 0:
            phrase = "un-labeled"
            try:
                list_comm = cluster[phrase]
                list_comm.append(comments[i])
                list_comm = list(set(list_comm))
                cluster[phrase] = list_comm
            except KeyError:
                cluster[phrase] = [comments[i]]

    return cluster, (len(comments) - len(cluster["un-labeled"])) / float(len(comments))
