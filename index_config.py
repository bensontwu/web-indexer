import configparser


class IndexConfig:
    def __init__(self, config_file_name):
        config = configparser.ConfigParser()
        config.read(config_file_name)

        index_file_names = config['INDEX_FILE_NAMES']
        partial_index_file_names = config['PARTIAL_INDEX_FILE_NAMES']
        index_location = config['INDEX_LOCATION']
        documents_location = config['DOCUMENTS_LOCATION']
        system_config = config['SYSTEM_CONFIG']

        self._input_dir_name = documents_location['INPUT_DIR']
        self._output_dir_name = index_location['OUTPUT_DIR']
        self._index_file_name = index_file_names['INVERTED_INDEX']
        self._token_locator_file_name = index_file_names['TOKEN_LOCATOR']
        self._doc_id_map = index_file_names['DOC_ID_MAP']
        self._partial_index_base_file_name = partial_index_file_names['INDEX_BASE']
        self._partial_index_token_locator_file_name = partial_index_file_names['TOKEN_LOCATOR']
        self._memory_threshold = int(system_config['MEMORY_THRESHOLD'])

    def get_output_dir(self) -> str:
        return self._output_dir_name

    def get_input_dir(self) -> str:
        return self._input_dir_name

    def get_index_file_path(self) -> str:
        return self._output_dir_name + "/" + self._index_file_name

    def get_token_locator_path(self) -> str:
        return self._output_dir_name + "/" + self._token_locator_file_name

    def get_doc_id_map_path(self) -> str:
        return self._output_dir_name + "/" + self._doc_id_map

    def get_partial_index_base_path(self) -> str:
        return self._output_dir_name + "/" + self._partial_index_base_file_name

    def get_partial_index_token_locator_path(self) -> str:
        return self._output_dir_name + "/" + self._partial_index_token_locator_file_name

    def get_memory_threshold(self) -> int:
        return self._memory_threshold
