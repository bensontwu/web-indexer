from utils import get_file_names
from doc_parse import get_json_from_file, get_html_content_from_json, get_url_from_json, dump_json_to_file
from tokenizer import tokenize, compute_word_frequencies
import sys
import psutil

def create_term(index_dict, token_dict, doc_id):
    for i, j in token_dict.items():
        if i not in index_dict:
            index_dict[i] = [(doc_id, j)]
        else:
            index_dict[i].append((doc_id, j))

def time_to_offload() -> bool:
    return psutil.virtual_memory().percent > 95

def get_partial_index_file_name(partial_index_count: int) -> str:
    return f"index-{partial_index_count}.json"

def main(directory_name):
    inverted_index = {}
    partial_index_count = 0
    doc_map = {}
    doc_id = 0
    file_names = get_file_names(directory_name)
    for file in file_names:
        # add the term to the inverted index
        json_dict = get_json_from_file(file)
        html_content = get_html_content_from_json(json_dict)
        tokens = tokenize(html_content)
        word_freqs = compute_word_frequencies(tokens)
        create_term(inverted_index, word_freqs, doc_id)
        
        # add the url and document id mapping to the doc map
        url = get_url_from_json(json_dict)
        doc_map[doc_id] = url
        doc_id += 1

        # offload the index if need be
        if time_to_offload():
            dump_json_to_file(inverted_index, get_partial_index_file_name(partial_index_count))
            inverted_index = {}; partial_index_count += 1
    
        print(f"Completed file: {file}")

    # offload the index
    dump_json_to_file(inverted_index, get_partial_index_file_name(partial_index_count))

    # print the document id mapping
    dump_json_to_file(doc_map, "json_mapping.json")

if __name__ == "__main__":
    directory_name = sys.argv[1]
    main(directory_name)
