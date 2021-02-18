# Get list of postings from index
def get_postings(index, query_term) -> list:
    try:
        return index[query_term]
    except KeyError:
        return []

# Creates a dictionary of postings
# for quicker intersection
# { doc_id, token_frequency }


def get_postings_dict(postings_list) -> dict:
    p_dict = {}
    for posting in postings_list:
        p_dict[posting[0]] = posting[1]
    return p_dict

# Sorts list of postings


def get_sorted_postings(postings_dict: dict) -> dict:
    return dict(sorted(postings_dict.items(), key=lambda posting: -posting[1]))

# # O(N)
# def doc_in_postings(doc_id: int, postings: list):
#     for posting in postings:
#         if doc_id == posting[0]:
#             return True
#     return False

# Creates combined dictionary of postings


def get_combined_postings(l_postings: dict, r_postings: dict) -> dict:
    final_postings = {}
    for doc_id in l_postings.keys():
        if doc_id in r_postings.keys():
            # add the frequencies together to get a combined token frequency for sorting
            final_postings[doc_id] = l_postings[doc_id] + r_postings[doc_id]
    return final_postings

# Self explainatory


def print_postings(postings_dict: dict, doc_mapping: dict, limit: int = None) -> None:
    print(doc_mapping)
    for i, (doc_id, token_freq) in enumerate(postings_dict.items()):
        if limit != None and i >= limit:
            break
        try:
            print(f"{doc_mapping[str(doc_id)]} with a freq of {token_freq}")
        except KeyError:
            print("key error")
            continue
