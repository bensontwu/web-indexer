from utils import get_file_names, url_is_valid
from doc_parse import get_json_from_file, get_html_content_from_json, get_url_from_json, dump_json_to_file
from tokenizer import tokenize, compute_word_frequencies
from json.decoder import JSONDecodeError
from datetime import datetime
from collections import defaultdict
import shutil
import json
import sys
import os

from index_config import IndexConfig


class InvertedIndexManager:

    def __init__(self, index_config: IndexConfig):
        self._index_config = index_config

        # partial index data structures
        self._partial_index_locator = defaultdict(list)
        self._partial_index_file_names = []

        # merged index data structures
        self._inverted_index = defaultdict(list)
        self._token_locator = {}

        # document id mapping information
        self._doc_id_map = {}
        self._doc_id = 0

    # Build the index
    def create_index(self):
        self._create_partial_indices()
        self._merge_indices()

    # query the index
    def get_postings(self, token, token_locator) -> list:

        # print("DEBUGGING TOKEN LOCATOR")
        # start_time = datetime.now()
        #
        # # for logging
        # end_time = datetime.now()
        # time_dif = end_time - start_time
        #
        # print(f"TOKEN LOCATOR TOOK {time_dif.microseconds / 1000} milliseconds")

        try:
            pos = token_locator[token]
        except KeyError:
            return []

        with open(self._index_config.get_index_file_path(), 'r') as f:
            f.seek(pos, 0)
            index_entry = json.loads(f.readline())
            return index_entry[token]

    # Return: a list of the partial index file names
    def _create_partial_indices(self):
        # for logging
        start_time = datetime.now().strftime('%H:%M:%S')

        # get the location of the documents and get all of the files inside
        file_names = get_file_names(self._index_config.get_input_dir())
        for file in file_names:
            try:

                self._add_document_to_index(file)

                # offload the index if need be
                if self._time_to_offload():
                    # offload to the partial index
                    self._offload_to_partial_index()

                # logging
                if self._doc_id % 100 == 0:
                    print(f"Current memory size: {sys.getsizeof(self._inverted_index)}")
                    print(f"Completed 100 files... current file: {file}")

            except JSONDecodeError:
                print(f"JSONDecodeError: Skipping file {file}")
                continue
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError: Skipping file {file}")
                continue

        # offload the index
        self._offload_to_partial_index()

        # print the document id mapping
        dump_json_to_file(self._doc_id_map, self._index_config.get_doc_id_map_path())

        # logging
        print(f"Started at: {start_time}")
        print(f"Partial indices!: {self._partial_index_file_names}")
        print(f"Completed!: {datetime.now().strftime('%H:%M:%S')}")

    def _add_document_to_index(self, file):
        # get info from document
        json_dict = get_json_from_file(file)
        url = get_url_from_json(json_dict)

        # skip this document if the url is not valid
        if not url_is_valid(url):
            return

        # add the document to the index
        html_content = get_html_content_from_json(json_dict)
        content_tokens, strong_tokens, title_tokens, h1_tokens, h2_tokens, h3_tokens, bold_tokens = tokenize(html_content)
        token_freqs = compute_word_frequencies(content_tokens, strong_tokens, title_tokens, h1_tokens, h2_tokens, h3_tokens, bold_tokens)
        for token, frequency in token_freqs.items():
            self._inverted_index[token].append((self._doc_id, frequency))

        # add the url and document id mapping to the doc map
        self._doc_id_map[self._doc_id] = url
        self._doc_id += 1

    def _get_partial_index_file_name(self, partial_index_count: int) -> str:
        return f"{self._index_config.get_partial_index_base_path()}-{partial_index_count}.json"

    # Steps:
    # 1. Open all file objects
    # 2. Iterate each token in token_file_location.txt and get list of where that is stored.
    # 3. Look for the file and its position inside its list.
    # 4. Store founded value into the total inverted index.
    # 5. Store its total inverted index.
    def _merge_indices(self):
        # logging
        print(f"Merge started: {datetime.now().strftime('%H:%M:%S')}")

        partial_index_file_objs = []

        # Open each partial index file and store its object inside list
        for file_name in self._partial_index_file_names:
            partial_index_file_objs.append(open(file_name, 'r'))

        # key = token, values = list of locations such as [[0,0],[1,13],[2,0]]
        # Each list represents [file number, location in the file]
        for token, locations in self._partial_index_locator.items():
            for (file_num, location) in locations:
                # Seek location=value[1] in the file=value[0]
                # Set the file pointer. seek(location, 0=absolute position)
                partial_index_file_objs[file_num].seek(location, 0)
                # Example of line: "{word: [[0,0],[1,13],[2,0]]}"
                line = partial_index_file_objs[file_num].readline()

                # Use json encoder to convert string into python dict object
                index_entry = json.loads(line)
                for posting in index_entry[token]:
                    # Add to the total inverted index
                    self._inverted_index[token].append(posting)

            # check if it's time to offload
            if self._time_to_offload():
                new_index_entry_positions = self._offload_index_to_file(self._index_config.get_index_file_path())
                # update the index entry locator
                self._token_locator.update(new_index_entry_positions)

        # offload
        new_index_entry_positions = self._offload_index_to_file(self._index_config.get_index_file_path())
        # update the index entry locator
        self._token_locator.update(new_index_entry_positions)

        # write the locator to a file
        dump_json_to_file(self._token_locator, self._index_config.get_token_locator_path())

        # logging
        print(f"Merge finished: {datetime.now().strftime('%H:%M:%S')}")

    def _time_to_offload(self) -> bool:
        return sys.getsizeof(self._inverted_index) > self._index_config.get_memory_threshold()

    # Returns a dict of tokens mapped to their position in the index file
    # Return: [token: position]
    def _offload_index_to_file(self, file_name: str) -> dict:

        print(f"Offloading! {file_name}")
        index_entry_positions = {}

        with open(file_name, 'a') as f:
            # get current file position
            file_position = f.tell()
            # Store inverted index to the file in the specific form
            # each line will be a dict for each index entry {token: [postings]}
            for token, postings in self._inverted_index.items():
                index_entry = json.dumps({token: postings})
                f.write(index_entry + '\n')

                # Store token and its position (which file and position inside that file)
                index_entry_positions[token] = file_position

                # Append position. Position is the number of characters
                # from the start of file.
                file_position += len(index_entry + '\n') + 1

        # reset the index
        self._inverted_index.clear()

        return index_entry_positions

    # Similar to offload to index, but does extra work
    # Updates the partial index file locator with the positions and file index
    def _offload_to_partial_index(self) -> int:
        # get the file name for the partial index file
        file_name = self._get_partial_index_file_name(len(self._partial_index_file_names))
        # offload to the index
        new_index_positions = self._offload_index_to_file(file_name)
        # update the partial index token file locator
        for token, position in new_index_positions.items():
            self._partial_index_locator[token].append((len(self._partial_index_file_names), position))

        # save the file name
        self._partial_index_file_names.append(file_name)


def main():
    # get config
    config_file_name = sys.argv[1]
    index_config = IndexConfig(config_file_name)

    output_dir_path = os.path.join(os.getcwd(), index_config.get_output_dir())

    if os.path.isdir(output_dir_path):
        decision = input("Existing index folder detected, this will be overwritten, do you want to continue? y/n\n")
        if decision.lower() == "y":
            shutil.rmtree(output_dir_path)
        else:
            return

    os.mkdir(output_dir_path)

    # create index object
    inverted_index_manager = InvertedIndexManager(index_config)

    # create the actual index files
    inverted_index_manager.create_index()


if __name__ == "__main__":
    main()
