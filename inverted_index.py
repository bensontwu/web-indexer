import json
import psutil

# Stores inverted index into each file
def store_index_json(documents, token_freq):

	inv_idx = {}

	file_num = 0
	docID = 0

	for document in documents:

		for token in document:

			if token in inv_idx:
				inv_idx[token].append([docID,token_freq[token]])
			else:
				inv_idx[token] = [[docID, token_freq[token]]]

		docID+=1

		# Used for RAM Check. Turned off for now.
		# if psutil.virtual_memory().percent > 95:

		# Sort by dictionary keys alphabetically
		# inv_idx = sorted(inv_idx.items())

		with open('inv' + str(file_num) + '.json', 'w') as f:
			json.dump(inv_idx, f, sort_keys=True, indent=4)

		inv_idx = {}
		file_num+=1

documents = [["word", "in4matx"], ["abcd", "indexaa"]]
token_freq = {"word":3, "in4matx":5, "abcd":5, "indexaa":3}

store_index_json(documents, token_freq)


def merge_index(file_num):

	for i in range(0, file_num):
		with open('inv'+str(i)+'.json', 'r') as f:

			inv_idx = json.load(f)

			# for s in f:
			# 	# s = s.replace("\'","\"")
			# 	d = json.loads(s)
			# 	print(d.keys())


merge_index(2)




# d = {'word':2, 'daa':3}

# with open('d.json', 'w') as f:
# 	json.dump(d, f, sort_keys=True, indent=4)
# 	json.dump(q, f, sort_keys=True, indent=4)

# with open('d.json') as f:
# 	for line in f:
# 		j_content = json.loads(line)

# 		print(j_content)


# d = {"a":1,"b":2}

# # for item in d:
# # 	print(dct{key:value})


# from itertools import islice

# for key, value in islice(d.items(), 2):
# 	print(key)  