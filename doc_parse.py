import json

def get_json_from_file(file_name: str) -> dict:
    with open(file_name, "r") as f:
        return json.load(f)

def dump_json_to_file(json_dict: dict, file_name: str) -> dict:
    with open(file_name, "w") as f:
        json.dump(json_dict, f)

def get_url_from_json(json_dict: dict) -> str:
    return json_dict['url']

def get_html_content_from_json(json_dict: dict) -> str:
    return json_dict['content']