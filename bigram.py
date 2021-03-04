from collections import Counter

tokens_lst = ["word", "word", "word", "b", "aaa", "aaa", "aaa", "aaa"]
bigrams_lst = list()

for i in range(0, len(tokens_lst)-1):
	bigrams_lst.append(tokens_lst[i] + tokens_lst[i+1])

print(bigrams_lst)

bigrams_count = Counter(bigrams_lst).most_common(2)

top_bigrams_lst = [word for word, count in bigrams_count]

print(top_bigrams_lst)


