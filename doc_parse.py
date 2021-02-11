import json

def get_json_from_file(file_name: str) -> dict:
    with open(file_name, "r") as f:
        return json.load(f)

def dump_json_to_file(json_dict: dict, file_name: str) -> dict:
    with open(file_name, "w") as f:
        json.dump(json_dict, f)