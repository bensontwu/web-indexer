import nltk.stem
import re
from collections import defaultdict
from bs4.element import Comment
from bs4 import BeautifulSoup


def tokenize_text(visible_texts) -> list:
    final_tokens = []
    s = nltk.stem.PorterStemmer()

    for text in visible_texts:
        line = text.lower()
        tokens = re.split("[^A-Za-z0-9']", line)
        for tok in tokens:
            stemmed_word = s.stem(tok)
            if stemmed_word != "":
                final_tokens.append(stemmed_word)

    return final_tokens


def convert_list_tokens(lst) -> list:
    # All text within strong tag
    text = ' '.join(lst)
    tokens = tokenize_text(text)

    return tokens


def tokenize(html) -> list:
    soup = BeautifulSoup(html, 'html.parser')

    # Get texts of the content and tokenize it -------------------
    texts = soup.findAll(text=True)
    visible_texts = filter(_elem_check, texts)

    content_tokens = tokenize_text(visible_texts)

    # Get texts of the strong tag and tokenize it ----------------
    strong_lst = soup.findAll("strong")
    strong_lst = [i.get_text() for i in strong_lst]

    strong_tokens = convert_list_tokens(strong_lst)

    # All words within h1 tag ----------------------------------
    h1_lst = soup.findAll("h1")
    h1_lst = [i.get_text() for i in h1_lst]

    h1_tokens = convert_list_tokens(h1_lst)

    # All words within h2 tag ----------------------------------
    h2_lst = soup.findAll("h2")
    h2_lst = [i.get_text() for i in h2_lst]

    h2_tokens = convert_list_tokens(h2_lst)

    # All words within h3 tag ----------------------------------
    h3_lst = soup.findAll("h3")
    h3_lst = [i.get_text() for i in h3_lst]

    h3_tokens = convert_list_tokens(h3_lst)

    # All words within b tag ----------------------------------
    bold_lst = soup.findAll("b")
    bold_lst = [i.get_text() for i in bold_lst]

    bold_tokens = convert_list_tokens(bold_lst)

    # All text within title tag ----------------------------------
    title = soup.find("title")
    if title != None:
        title_tokens = tokenize_text(title.get_text())
    else:
        title_tokens = []

    return content_tokens, strong_tokens, title_tokens, h1_tokens, h2_tokens, h3_tokens, bold_tokens


def compute_word_frequencies(content_tokens, strong_tokens, title_tokens, h1_tokens, h2_tokens, h3_tokens, bold_tokens):
    final_dict = defaultdict(int)

    for tok in content_tokens:
        final_dict[tok] += 1

    for tok in bold_tokens:
        final_dict[tok] += 2

    for tok in strong_tokens:
        final_dict[tok] += 3

    for tok in h3_tokens:
        final_dict[tok] += 4

    for tok in h2_tokens:
        final_dict[tok] += 5

    for tok in h1_tokens:
        final_dict[tok] += 6

    for tok in title_tokens:
        final_dict[tok] += 10

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