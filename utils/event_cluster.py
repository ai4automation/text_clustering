import argparse
import csv
import json
import logging
import sys

import utils.clustering as cluster


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename",
                        help="csv file with event and comments", metavar="FILE", required=True)
    parser.add_argument("-c", "--comment_field", dest="comment_field",
                        help="comments field name in header", metavar="C", required=True)
    parser.add_argument("-e", "--event_field", dest="event_field",
                        help="event field name in header", metavar="E", required=True)
    return parser


def reverse_dictionary(input_dict):
    out = {}
    for v in input_dict.values():
        for value in v:
            if value not in out:
                out[value] = []

    for i in input_dict:
        for j in out:
            if j in map(lambda x: x, input_dict[i]):
                out[j].append(i)
                out[j].sort()
    return out


def read_event_comment_dict(filename, comment_field, event_field):
    # Reads file and generates a dictionary for event and comments
    event_comment_dict = {}
    with open(filename, "r") as fobj:
        reader = csv.reader(fobj)
        header = next(reader)
        try:
            c_i = header.index(comment_field)
            e_i = header.index(event_field)
        except ValueError:
            raise ValueError('Incorrect comment/event field.')
        logging.getLogger().info(header)
        logging.getLogger().info("{} is comments field idx, {} is event field idx".format(c_i, e_i))
        print("{} is comments field idx, {} is event field idx".format(c_i, e_i))
        for row in reader:
            try:
                key = row[e_i]
                if len(row[c_i]) != 0:
                    if key not in event_comment_dict:
                        event_comment_dict[key] = []
                    event_comment_dict[key].append(row[c_i])
            except IndexError:
                pass

        logging.getLogger().info("Length of event dictionary: {}".format(len(event_comment_dict)))

    return event_comment_dict


def logger_init():
    logging.getLogger().setLevel(logging.INFO)
    root = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def cluster_comments_for_each_event(event_comment_dict):
    # Hash of Hashes: Key for the first is event name, and for value key is key-phrase
    event_keyphrase_dict = {}
    logging.getLogger().debug("Actions for which comments are present:{}".format(event_comment_dict.keys()))
    for event in event_comment_dict.keys():
        print(len(event_comment_dict[event]))
        json_string = json.dumps(event_comment_dict[event])
        # logging.getLogger().info(json_string);

        keyphrase_dict, _ = cluster.find_labels(json_string, coverage=False)

        comment2keyphrase_dict = reverse_dictionary(keyphrase_dict)

        logging.getLogger().debug("Key phrases for comments:{}".format(keyphrase_dict.keys()))

        event_keyphrase_dict[event] = comment2keyphrase_dict
    return event_keyphrase_dict


def write_output_csv(filename, comment_field, event_field, event_keyphrase_dict):
    derived_filename = filename[:-4] + '_derived.csv'

    with open(filename, "r") as fobj:
        reader = csv.reader(fobj)
        header = next(reader)
        c_i = header.index(comment_field)
        e_i = header.index(event_field)
        header.append("DERIVED_ACTION")
        f = open(derived_filename, 'w')
        writer = csv.writer(f, delimiter=',')
        print(header)
        writer.writerow(header)

        for row in reader:
            comment = row[c_i]
            event = row[e_i]
            if event in event_keyphrase_dict:
                comment2keyphrase_dict = event_keyphrase_dict[event]
                if comment in comment2keyphrase_dict:
                    keyphrases = comment2keyphrase_dict[comment]
                    for p in keyphrases:
                        new_row = row
                        new_row.append(p)
                        writer.writerow(new_row)
    return derived_filename


def run_e2e(filename, comment_field, event_field):
    event_comment_dict = read_event_comment_dict(filename, comment_field, event_field)
    event_keyphrase_dict = cluster_comments_for_each_event(event_comment_dict)
    derived_file = write_output_csv(filename, comment_field, event_field, event_keyphrase_dict)
    return derived_file


if __name__ == "__main__":
    args = get_parser().parse_args()
    logger_init()
    run_e2e(args.filename, args.comment_field, args.event_field)
