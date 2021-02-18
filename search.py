import sys

from doc_parse import get_json_from_file
from posting import get_combined_postings, get_postings, get_postings_dict, get_sorted_postings, print_postings

# Input loop
if __name__ == "__main__":
    index_file_name = sys.argv[1]
    index_mapping_name = sys.argv[2]
    index = get_json_from_file(index_file_name)
    mapping = get_json_from_file(index_mapping_name)

    while True:
        query_string = input("Please search me!\n>>> ")
        query_terms = query_string.split()

        # get matching postings from each query term
        posting_dicts = []
        for query_term in query_terms:
            postings = get_postings(index, query_term)
            p_dict = get_postings_dict(postings)
            posting_dicts.append(p_dict)
        
        # get the combined postings from the multiple terms i.e. AND operation
        combined_postings = posting_dicts[0]
        for p_dict in posting_dicts[1:]:
            combined_postings = get_combined_postings(combined_postings, p_dict)
        
        # sort the postings
        sorted_postings = get_sorted_postings(combined_postings)

        # print the sorted postings
        print_postings(sorted_postings, mapping)
        


