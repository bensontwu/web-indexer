import json

def get_json_from_file(file_name: str) -> dict:
    with open(file_name) as f:
        return json.load(f)