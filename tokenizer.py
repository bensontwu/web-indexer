import nltk.stem
import re
from collections import defaultdict
from bs4.element import Comment
from bs4 import BeautifulSoup
nltk.stem.PorterStemmer()
        
def tokenize(html) -> list:
    s = nltk.stem.PorterStemmer()
    final_tokens = []
    soup = BeautifulSoup(html)

    texts = soup.findAll(text=True)
    visible_texts = filter(_elem_check, texts)
    for text in visible_texts:
        line = text.lower()
        tokens = re.split("[^A-Za-z0-9']", line)
        for tok in tokens:
            stemmed_word = s.stem(tok)
            final_tokens.append(stemmed_word)

def compute_word_frequencies(tokens):
    final_dict = defaultdict(int)
    for tok in tokens:
        final_dict[tok] += 1
    return final_dict

# This function return true
# 1. if text element is not comment inside html.
# 2. if text element is not inside invalid html tags.
# Refered to : https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def _elem_check(element):
    if isinstance(element, Comment):
        return False
    elif element.parent.name in ['style', 'script', 'head', 'meta', '[document]', 'a']:
        return False
    return True