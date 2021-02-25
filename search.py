import sys
import json

from index_config import IndexConfig
from inverted_index import InvertedIndexManager
from doc_parse import get_json_from_file
from posting import get_combined_postings, get_postings, get_scored_postings, get_sorted_postings, print_postings


# Returns dictionary of query term to list of postings
# Return: [query_term: [[doc_id, freq], [...], ... ]
def get_index_entry(query_term: str) -> dict:
    token_locator = get_json_from_file('merged_token_locator.json')

    with open('merged_index.txt', 'r') as f:
        position = token_locator[query_term]
        f.seek(position, 0)

        index_entry = json.loads(f.readline())
        return index_entry


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
        query_terms = query_string.split()

        # get matching postings from each query term
        posting_dicts = []
        for query_term in query_terms:
            postings = inverted_index_manager.get_postings(query_term)
            p_dict = get_scored_postings(postings, len(doc_id_map), len(postings))
            posting_dicts.append(p_dict)
        
        # get the combined postings from the multiple terms i.e. AND operation
        combined_postings = posting_dicts[0]
        for p_dict in posting_dicts[1:]:
            combined_postings = get_combined_postings(combined_postings, p_dict)
        
        # sort the postings
        sorted_postings = get_sorted_postings(combined_postings)

        # print the sorted postings
        print_postings(sorted_postings, doc_id_map)
        


