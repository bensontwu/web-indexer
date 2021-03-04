import os
from urllib.parse import urlparse
import re


def get_file_names(directory_name: str) -> list:
    file_names = []
    for root, _, files in os.walk(directory_name):
        for name in files:
            file_names.append(os.path.join(root, name))
    return file_names


def url_is_valid(url: str) -> bool:
    try:
        parsed = urlparse(url)

        # skip non http or https schemes
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # skip fragments
        if len(parsed.fragment) != 0:
            return False

        # skip most non-HTML files
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|txt|odc)$", parsed.path.lower()):
            return False
        
        # skip /index.html as we index the root already
        if re.match(r".*/index.html$", parsed.path.lower()):
            return False

        return True

    except TypeError:
        print("TypeError for ", parsed)
        raise

# def test_dev_file_names():
#     directory_name = "DEV"
#     file_names = get_dev_file_names(directory_name)
#     print(file_names)

# test_dev_file_names()