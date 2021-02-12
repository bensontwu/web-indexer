from doc_parse import get_json_from_file

if __name__ == "__main__":
    index = get_json_from_file("index-0.json")
    print(f"Index # of unique tokens: {len(index.keys())}")