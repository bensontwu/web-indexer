import os

def get_file_names(directory_name: str) -> list:
    file_names = []
    for root, _, files in os.walk(directory_name):
        for name in files:
            file_names.append(os.path.join(root, name))
    return file_names

# def test_dev_file_names():
#     directory_name = "DEV"
#     file_names = get_dev_file_names(directory_name)
#     print(file_names)

# test_dev_file_names()