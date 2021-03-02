import sys
import json
import math
from collections import defaultdict
from datetime import datetime

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

    while True:
        query_string = input("Please search me!\n>>> ")

        # for logging
        start_time = datetime.now()

        query_terms = query_string.split()

        # [doc_id: [w_tf]]
        doc_vectors = defaultdict(list)
        # [term: [posting]] intermediary dict for building doc_vectors later
        term_postings = {}
        # [tf_id]
        query_vector = []

        # get matching postings from each query term
        for query_term in query_terms:
            # get postings for each term
            postings = inverted_index_manager.get_postings(query_term)
            # append to term postings
            term_postings[query_term] = postings
            # check if no postings contain query term
            if len(postings) == 0:
                query_vector.append(0)
            else:
                # build query vector
                query_vector.append(tf_idf(1, len(doc_id_map), len(postings)))

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
        print_postings(sorted_postings, doc_id_map, limit=5)

        # for logging
        end_time = datetime.now()
        time_dif = end_time - start_time

        print(f"Query took {time_dif.microseconds / 1000} milliseconds")


