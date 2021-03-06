import math

# Get list of postings from index
def get_postings(index, query_term) -> list:
    try:
        return index[query_term]
    except KeyError:
        return []


def tf_idf(term_freq: int, total_docs: int, doc_freq: int) -> float:
    tf = 1 + math.log(term_freq, 10)
    idf = math.log(total_docs/doc_freq, 10)
    return tf * idf


# Creates a dictionary of postings
# for quicker intersection
# { doc_id, tf-idf }
def get_scored_postings(postings_list, total_docs, doc_freq) -> dict:
    p_dict = {}
    for posting in postings_list:
        p_dict[posting[0]] = tf_idf(posting[1], total_docs, doc_freq)
    return p_dict


# Sorts list of postings
def get_sorted_postings(postings_dict: dict) -> dict:
    return dict(sorted(postings_dict.items(), key=lambda posting: -posting[1]))


# Combines the scores for each dict of postings
def get_combined_postings(l_postings: dict, r_postings: dict) -> dict:
    final_postings = {}
    for doc_id in l_postings.keys():
        if doc_id in r_postings.keys():
            # add the frequencies together to get a combined token frequency for sorting
            final_postings[doc_id] = l_postings[doc_id] + r_postings[doc_id]
    return final_postings


# Self explanatory
def print_postings(postings_dict: dict, doc_mapping: dict, limit: int = None) -> None:
    for i, (doc_id, token_freq) in enumerate(postings_dict.items()):
        if limit != None and i >= limit:
            break
        try:
            print(f"{doc_mapping[str(doc_id)]} with a tf-idf score of {token_freq}")
        except KeyError:
            print("key error")
            continue
