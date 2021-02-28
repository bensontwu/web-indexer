import nltk.stem
import re
from collections import defaultdict
from bs4.element import Comment
from bs4 import BeautifulSoup
nltk.stem.PorterStemmer()
        

def tokenize_text(visible_texts) -> list:

    final_tokens = []

    for text in visible_texts:
        line = text.lower()
        tokens = re.split("[^A-Za-z0-9']", line)
        for tok in tokens:
            stemmed_word = s.stem(tok)
            if stemmed_word != "":
                final_tokens.append(stemmed_word)

    return final_tokens


def tokenize(html) -> list:
    s = nltk.stem.PorterStemmer()
    final_tokens = []
    soup = BeautifulSoup(html, 'html.parser')

    # Get texts of the content and tokenize it -------------------
    texts = soup.findAll(text=True)
    visible_texts = filter(_elem_check, texts)
    
    content_tokens = tokenize_text(visible_texts)

    # Get texts of the strong tag and tokenize it ----------------
    strong_lst = html.findAll("strong")
    strong_lst = [i.get_text() for i in strong_lst]

    # All text within strong tag
    strong_text = ' '.join(strong_lst)
    strong_tokens = tokenize_text(strong_text)

    # All text within title tag ----------------------------------
    title_text = html.find("title").get_text()
    title_tokens = tokenize_text(title_text)

    return final_tokens, strong_tokens, title_tokens


def compute_word_frequencies(tokens, strong_tokens, title_tokens):
    final_dict = defaultdict(int)
    for tok in tokens:
        final_dict[tok] += 1

    for tok in strong_tokens:
        final_dict[tok] += 1

    for tok in title_tokens:
        final_dict[tok] += 2

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