from utils import get_file_names, url_is_valid
from doc_parse import get_json_from_file, get_html_content_from_json, get_url_from_json, dump_json_to_file
from tokenizer import tokenize, compute_word_frequencies
from json.decoder import JSONDecodeError
from datetime import datetime
from collections import defaultdict
import json
import sys
import psutil


def create_term(index_dict, token_dict, doc_id):
    for token, frequency in token_dict.items():
        if token not in index_dict:
            index_dict[token] = [(doc_id, frequency)]
        else:
            index_dict[token].append((doc_id, frequency))


def time_to_offload() -> bool:
    return psutil.virtual_memory().percent > 50


def get_partial_index_file_name(partial_index_count: int) -> str:
    return f"{get_index_dir()}index-{partial_index_count}.json"


def get_index_dir() -> str:
    return "index/"


# Return: a list of the partial index file names
def create_partial_indices(directory_name: str) -> list:
    # logging
    print(f"Started!: {datetime.now().strftime('%H:%M:%S')}")

    inverted_index, doc_map = {}, {}
    partial_index_token_file_locator = defaultdict(list)
    partial_index_count, doc_id = 0, 0
    partial_index_file_names = []

    file_names = get_file_names(directory_name)
    for file in file_names:
        try:
            # add the term to the inverted index
            json_dict = get_json_from_file(file)
            url = get_url_from_json(json_dict)

            # skip this document if the url is not valid
            if not url_is_valid(url):
                continue

            # create term in index
            html_content = get_html_content_from_json(json_dict)
            tokens = tokenize(html_content)
            word_freqs = compute_word_frequencies(tokens)
            create_term(inverted_index, word_freqs, doc_id)

            # add the url and document id mapping to the doc map
            doc_map[doc_id] = url
            doc_id += 1

            # offload the index if need be
            if time_to_offload():
                # offload to the partial index
                offload_to_partial_index(inverted_index, partial_index_token_file_locator,
                                         partial_index_count, partial_index_file_names)
                # reset the index and increment the partial index count
                inverted_index.clear(); partial_index_count += 1
            
            # logging
            if doc_id % 100 == 0:
                print(f"Completed 100 files... current file: {file}")

        except JSONDecodeError:
            print(f"JSONDecodeError: Skipping file {file}")
            continue
        except UnicodeDecodeError:
            print(f"UnicodeDecodeError: Skipping file {file}")
            continue

    # offload the index
    offload_to_partial_index(inverted_index, partial_index_token_file_locator,
                             partial_index_count, partial_index_file_names)

    # print the document id mapping
    dump_json_to_file(doc_map, f"{get_index_dir()}doc_id_map.json")

    # Dump token_file_loc which is dictionary object into text file
    # by converting dictionary into string.
    dump_json_to_file(partial_index_token_file_locator, f"{get_index_dir()}partial_file_token_locator.json");

    # logging
    print(f"Partial indices!: {partial_index_file_names}")
    print(f"Completed!: {datetime.now().strftime('%H:%M:%S')}")

    return partial_index_file_names


# Steps:
# 1. Open all file objects
# 2. Iterate each token in token_file_location.txt and get list of where that is stored.
# 3. Look for the file and its position inside its list.
# 4. Store founded value into the total inverted index.
# 5. Store its total inverted index.
def merge_indices(partial_index_file_names: list):
    # logging
    print(f"Merge started: {datetime.now().strftime('%H:%M:%S')}")

    partial_index_file_objs = []
    token_locator = {}
    inverted_index = defaultdict(list)

    # Open the file which stores hash[token] = file location
    partial_index_token_file_locator = get_json_from_file(f'{get_index_dir()}partial_file_token_locator.json');

    # Open each partial index file and store its object inside list
    for file_name in partial_index_file_names:
        partial_index_file_objs.append(open(file_name, 'r'))

    # key = token, values = list of locations such as [[0,0],[1,13],[2,0]]
    # Each list represents [file number, location in the file]
    for token, locations in partial_index_token_file_locator.items():
        for (file_num, location) in locations:
            # Seek location=value[1] in the file=value[0]
            # Set the file pointer. seek(location, 0=absolute position)
            partial_index_file_objs[file_num].seek(location, 0)
            # Example of line: "{word: [[0,0],[1,13],[2,0]]}"
            line = partial_index_file_objs[file_num].readline()

            # Use json encoder to convert string into python dict object
            index_entry = json.loads(line);
            for posting in index_entry[token]:
                # Add to the total inverted index
                inverted_index[token].append(posting)

        # check if it's time to offload
        if time_to_offload():
            new_index_entry_positions = offload_to_index(inverted_index, f'{get_index_dir()}merged_index.txt')
            # update the index entry locator
            token_locator.update(new_index_entry_positions)
            # clear the in-memory index
            inverted_index.clear()

    # write the locator to a file
    dump_json_to_file(token_locator, f'{get_index_dir()}merged_token_locator.json')

    # logging
    print(f"Merge finished: {datetime.now().strftime('%H:%M:%S')}")


# Returns a dict of tokens mapped to their position in the index file
# Return: [token: position]
def offload_to_index(inverted_index: dict, file_name: str) -> dict:
    index_entry_positions = {}

    with open(file_name, 'a') as f:
        # get current file position
        file_position = f.tell()
        # Store inverted index to the file in the specific form
        # each line will be a dict for each index entry {token: [postings]}
        for token, postings in inverted_index.items():
            index_entry = json.dumps({token: postings})
            f.write(index_entry + '\n')

            # Store token and its position (which file and position inside that file)
            index_entry_positions[token] = file_position

            # Append position. Position is the number of characters
            # from the start of file.
            file_position += len(index_entry + '\n') + 1

    return index_entry_positions


# Similar to offload to index, but does extra work
# Updates the partial index file locator with the positions and file index
def offload_to_partial_index(inverted_index: dict,
                             partial_index_token_file_locator: dict,
                             partial_index_count: str,
                             partial_index_file_names: list) -> int:
    file_name = get_partial_index_file_name(partial_index_count)
    partial_index_file_names.append(file_name)
    # offload to the index
    new_index_positions = offload_to_index(inverted_index, file_name)
    # update the partial index token file locator
    for token, position in new_index_positions.items():
        partial_index_token_file_locator[token].append((partial_index_count, position))


if __name__ == "__main__":
    document_directory_name = sys.argv[1]
    partial_index_file_names = create_partial_indices(document_directory_name)
    merge_indices(partial_index_file_names)
