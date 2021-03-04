import sys

def position(inv_idx, query_tokens):

	# Dictionary of each combination of words
	pos_dict = {}

	for i in range(0,len(query_tokens)):
		for j in range(i+1, len(query_tokens)):
			print(i,j)
			# Combination of tokens Ex: "Donald"+"Trump"
			comb_token = query_tokens[i] + query_tokens[j]

			if comb_token in pos_dict.keys():
				pos_dict[comb_token].append(j-i)
			else:
				pos_dict[comb_token] = [j-i]

	print(pos_dict)
	sys.exit()

	first_token = query_tokens.pop(0)

	# Get common docID between multiple inverted indices for query_tokens
	# Use set operation
	common_docs = set(inv_idx[first_token].keys())

	for token in query_tokens:
		if token in inv_idx.keys():
			common_docs.intersection_update(inv_idx[token].keys())

	pool = set()

	# Same words Ex: to "be" or not to "be"
	for token in query_tokens:
		for doc in common_docs:
			for diff in pos_dict[token].keys():
				#      list of positions + difference in the token
				copy = inv_idx[token][doc] + diff
				pool.intersection_update(copy + inv_idx[token][doc])


	# Different words Ex: "to" "be"

	print(pool)


	# for doc in common_docs:
	# 	token = query_tokens[0]

	# 	# for pos in inv_idx[token][doc]:
	# 	# 	print(pos)
	# 	pool.intersection_update(inv_idx[token][doc]+1)

	# 	token = query_tokens[1]

	# 	for pos in inv_idx[token][doc]:
	# 		pool.intersection_update(pos)

	# print(pool)



inv_idx = {}

# Test 1            Document:location
inv_idx["Donald"] = {1:[2,3], 2:[1,10]}
inv_idx["Trump"] = {0:[2,3], 2:[2,5]}

query_tokens = ["Donald", "Trump", "Trump", "Donald"]

position(inv_idx, query_tokens)



# Test 2
 			  # {DocID: [Position of the token inside its Doc]}
# inv_idx["to"] = {2:[1,2], 4:[8,16,190,429,433]}
# inv_idx["be"] = {1:[2,3], 4:[17,191,291,430,434,2]}
# inv_idx["or"] = {1:[2,3], 4:[1,2]}
# inv_idx["not"] = {1:[2,3], 2:[1,2]}

# query_tokens = ["to", "be", "or", "not", "to", "be"]






