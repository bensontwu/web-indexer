import sys
import json
import math
from collections import defaultdict
from datetime import datetime
import nltk.stem
import re

from index_config import IndexConfig
from inverted_index import InvertedIndexManager
from doc_parse import get_json_from_file
from posting import tf_idf
from posting import print_postings


# Returns dictionary of query term to list of postings
# Return: [query_term: [[doc_id, freq], [...], ... ]
def get_index_entry(query_term: str) -> dict:
    token_locator = get_json_from_file('merged_token_locator.json')

    with open('merged_index.txt', 'r') as f:
        position = token_locator[query_term]
        f.seek(position, 0)

        index_entry = json.loads(f.readline())
        return index_entry


def get_norm_constant(vector: list) -> float:
    s = 0
    for item in vector:
        s += item ** 2
    return math.sqrt(s)


def normalized(vector: list) -> list:
    normalized_vector = []
    norm_constant = get_norm_constant(vector)
    for item in vector:
        normalized_vector.append(item / norm_constant)
    return normalized_vector


def weighted_term_freq(term_freq: int) -> float:
    w_tf = 1 + math.log(term_freq, 10)
    return w_tf


def dot_product(v1: list, v2: list) -> float:
    dp = 0
    for i1, i2 in zip(v1, v2):
        dp += i1 * i2
    return dp


# Input loop
if __name__ == "__main__":
    # get config
    config_file_name = sys.argv[1]
    index_config = IndexConfig(config_file_name)

    # create the inverted index manager
    inverted_index_manager = InvertedIndexManager(index_config)

    # create the doc id map
    doc_id_map_file_name = index_config.get_doc_id_map_path()
    doc_id_map = get_json_from_file(doc_id_map_file_name)

    # initialize stemmer
    stemmer = nltk.stem.PorterStemmer()

    token_locator = get_json_from_file(index_config.get_token_locator_path())

    while True:
        query_string = input("Please search me!\n>>> ")

        # for logging
        start_time = datetime.now()

        query_terms = re.split("[^A-Za-z0-9']", query_string)
        query_terms = [stemmer.stem(term) for term in query_terms]
        # need to get query terms and how many time each term occurs in query
        # [term: term_frequency]
        query_term_freqs = defaultdict(int)
        for term in query_terms:
            query_term_freqs[term] += 1

        # [doc_id: [w_tf]]
        doc_vectors = defaultdict(list)
        # [term: [posting]] intermediary dict for building doc_vectors later
        term_postings = {}
        # [tf_id]
        query_vector = []

        # build the query_vector and term_postings
        for term, freq in query_term_freqs.items():
            # get postings for each term
            postings = inverted_index_manager.get_postings(term, token_locator)
            term_postings[term] = postings
            if len(postings) == 0:
                query_vector.append(0)
            else:
                # build query vector
                query_vector.append(tf_idf(freq, len(doc_id_map), len(postings)))

        # create the doc_vectors
        for term, postings in term_postings.items():
            for posting in postings:
                doc_vectors[posting[0]].append(weighted_term_freq(posting[1]))

        # apply normalize the vectors
        for doc_id, vector in doc_vectors.items():
            vector = normalized(vector)

        # [doc_id, score]
        doc_scores = {}
        # compute cosine similarity between query vector and each document vector
        for doc_id, doc_vector in doc_vectors.items():
            doc_scores[doc_id] = dot_product(doc_vector, query_vector)

        # get the documents in order of their relevance score
        sorted_postings = {doc_id: doc_vector for doc_id, doc_vector in
                           sorted(doc_scores.items(), key=lambda item: -item[1])}

        # print the postings
        print_postings(sorted_postings, doc_id_map, limit=10)

        # for logging
        end_time = datetime.now()
        time_dif = end_time - start_time

        print(f"Query took {time_dif.seconds} seconds, {time_dif.microseconds / 1000} milliseconds")


