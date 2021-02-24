import json, ijson
import psutil
import pickle


# This function store index into many partial files
# There is memory variable for test purpose.
def store_index(documents, token_freq):

	inv_idx, token_file_loc = {}, {}

	# pos is the position inside the file
	file_num, docID, pos = 0, 0, 0

	memory = 0

	for document in documents:
		for token in document:
			if token in inv_idx:
				inv_idx[token].append([docID,token_freq[token]])
			else:
				inv_idx[token] = [[docID, token_freq[token]]]

		docID+=1
		memory+=1

		# Used for RAM Check
		# if psutil.virtual_memory().percent > 5:
		if memory == 2:
			with open('inv' + str(file_num) + '.txt', 'w') as f:

				# Store inverted index to the file in the specific form
				# such as word [[1,2]] from {"word":[[1,2]]}
				# In this way, we can read each index easily later on.
				for key, value in inv_idx.items():
					f.write(str(key) + ' ' + str(value) + '\n')

					# Store token and its position (which file and position inside that file)
					if key in token_file_loc.keys():
						token_file_loc[key].append([file_num, pos])
					else:
						token_file_loc[key] = [[file_num, pos]]

					# Append position. Position is the number of characters
					# from the start of file.
					pos = pos + len(str(key) + ' ' + str(value) + '\n') + 1
			
				file_num+=1
				file_loc = 0

				inv_idx = {}
				memory=0
				pos=0

	with open('token_file_location.txt', 'w') as f:
		# Dump token_file_loc which is dictionary object into text file
		# by converting dictionary into string.
		f.write(json.dumps(token_file_loc))


# This function combines partial inverted index into one total inverted index
# by reading partial files and save it into one file.

# Steps:
# 1. Open all file objects
# 2. Iterate each token in token_file_location.txt and get list of where that is stored.
# 3. Look for the file and its position inside its list.
# 4. Store founded value into the total inverted index.
# 5. Store its total inverted index.
def merge_index(file_num):
	file_objs = list()
	inv_idx = {}

	# Open the file which stores hash[token] = file location
	with open('token_file_location.txt', 'r') as f:
		token_file_loc = json.loads(f.readline())

		# Open each partial index file and store its object inside list
		for i in range(0, file_num):
			file_objs.append(open('inv' + str(i) + '.txt', 'r'))

		# key = token, values = list of locations such as [[0,0],[1,13],[2,0]]
		# Each list represents [file number, location in the file]
		for key, values in token_file_loc.items():
			for value in values:
				# Seek location=value[1] in the file=value[0]
				# Set the file pointer. seek(location, 0=absolute position)
				file_objs[value[0]].seek(value[1], 0)
				# Example of line: "word [[0,0],[1,13],[2,0]]"
				line = file_objs[value[0]].readline()
				
				# Split and get last element which is "[[0,0],[1,13],[2,0]]"
				# Use json encoder to convert string into python list object
				for lst_val in json.loads(line.split(maxsplit=1)[1]):

					# Add to the total inverted index
					if key in inv_idx.keys():
						inv_idx[key].append(lst_val)
					else:
						inv_idx[key] = [lst_val]

		# Store total inverted index into one file at the end
		with open('total_inv_idx.txt', 'w') as f:

			# token and location
			file_loc_idx = {}
			# location inside the file
			loc = 0

			for key, value in inv_idx.items():
				temp_idx = {}
				temp_idx[key] = value

				f.write(json.dumps(temp_idx)+'\n')

				file_loc_idx[key] = loc
				loc = loc + len(json.dumps(temp_idx)) + 1

				inv_idx={}

		with open('total_inv_idx_loc.txt', 'w') as f:
			f.write(json.dumps(file_loc_idx)+'\n')


def read_one_idx(query_word):

	with open('total_inv_idx_loc.txt', 'r') as f:
		token_file_loc = json.loads(f.readline())

	with open('total_inv_idx.txt', 'r') as f:

		pos = token_file_loc[query_word]
		f.seek(pos, 0)

		dct_token = json.loads(f.readline())
		print(dct_token)


# Test case
documents = [["word", "in4matx"], ["abcd", "indexaa"], ["people", "iam"], ["iam","abcd"], ["people", "iam"], ["iam","abcd"]]
token_freq = {"word":3, "in4matx":5, "abcd":5, "indexaa":3, "people":1, "iam":2}

store_index(documents, token_freq)

# There were three text files to store partial index, so it's 3.
merge_index(3)

read_one_idx("word")



# ---------------------------------------------------------------------------------------------------------------------


# from itertools import islice

# def chunks(data, SIZE=10000):
# 	it = iter(data)
# 	for i in xrange(0, len(data), SIZE):
# 		yield {k:data[k] for k in islice(it, SIZE)}

# # Stores inverted index into each file
# def store_index_json(documents, token_freq):

# 	inv_idx = {}

# 	file_num = 0
# 	docID = 0

# 	for document in documents:

# 		for token in document:

# 			if token in inv_idx:
# 				inv_idx[token].append([docID,token_freq[token]])
# 			else:
# 				inv_idx[token] = [[docID, token_freq[token]]]

# 		docID+=1

# 		# Used for RAM Check. Turned off for now.
# 		# if psutil.virtual_memory().percent > 95:

# 		# Sort by dictionary keys alphabetically
# 		inv_idx = sorted(inv_idx.items())

# 		# for item in chunks({i:i for i in xrange(10)}, 3):


# 		with open('inv' + str(file_num) + '.json', 'w') as f:
# 			json.dump(inv_idx, f, indent=4)

# 		inv_idx = {}
# 		file_num+=1


# def store_index_pickle(documents, token_freq):

# 	inv_idx = {}

# 	file_num = 0
# 	docID = 0

# 	for document in documents:

# 		for token in document:

# 			if token in inv_idx:
# 				inv_idx[token].append([docID,token_freq[token]])
# 			else:
# 				inv_idx[token] = [[docID, token_freq[token]]]

# 		docID+=1

# 		# Used for RAM Check. Turned off for now.
# 		# if psutil.virtual_memory().percent > 95:

# 		# Sort by dictionary keys alphabetically
# 		# inv_idx = sorted(inv_idx.items())

# 		with open('inv' + str(file_num) + '.pickle', 'wb') as f:
# 			pickle.dump(inv_idx, f)

# 		inv_idx = {}
# 		file_num+=1



# def store_index_pickle_1000(documents, token_freq):

# 	inv_idx = {}

# 	file_num = 0
# 	docID = 0
# 	num_doc = 0

# 	memory=0

# 	for document in documents:

# 		for token in document:

# 			if token in inv_idx:
# 				inv_idx[token].append([docID,token_freq[token]])
# 			else:
# 				inv_idx[token] = [[docID, token_freq[token]]]

# 		docID+=1

# 		# Number of document processed before dumping in pickle file
# 		num_doc+=1

# 		# Partially save 100 documents (objects) into same pickle file,
# 		# so that we can load 1000 documents (objects) later when we need to merge indices
# 		# https://stackoverflow.com/questions/20716812/saving-anSd-loading-multiple-objects-in-pickle-file
# 		if num_doc == 2:
# 			with open('inv' + str(file_num) + '.pickle', 'ab') as f:
# 				print(inv_idx, file_num)
# 				pickle.dump(inv_idx, f)
# 			num_doc = 0

# 			inv_idx={}

# 			file_num+=1

# 		# Used for RAM Check
# 		# if psutil.virtual_memory().percent > 90:
# 		# if memory == 1:
# 		# 	with open('inv' + str(file_num) + '.pickle', 'ab') as f:
# 		# 		pickle.dump(inv_idx, f)
			
# 		# 		file_num+=1
# 		# 		num_doc = 0
# 		# 		memory=0

# 		# 		inv_idx = {}

# 		memory+=1


# s = 'iam [[2, 2], [3, 2]]\n'
# l = json.loads(s.split(maxsplit=1)[1])

# print(l)

# lst = []

# f = open('inv0.txt', 'r')
# f.seek(2)

# print(f.readline())

# for i in range(0, 3):
# 	f = open('inv' + str(i) + '.txt', 'r')
# 	lst.append(f)

# for a in lst:
# 	print(a.readline())

# print(lst)


# with open('inv0.txt', 'r') as f:
# 	f.seek(15, 0)
# 	print(f.readline())

# import itertools


# chunk_lst = []

# def merge_index(file_num):
# 	# How many division 
# 	for j in range(0,10):
# 		for i in range(0, file_num):
# 			with open('inv'+str(i)+'.pickle', 'rb') as f:

# 				# Check whether it is the end of file
# 				try:
# 					chunk_lst.append(pickle.load(f))

# 					if i == 0 and j==0:
# 						merged_idx = obj
# 					else:
# 						for key, value in obj.items():		
# 							if key in merged_idx:
# 								for val in value:
# 									merged_idx[key].append(val)
# 							else:
# 								merged_idx[key] = value
# 				except EOFError:
# 					print("End of file")

# 			with open('total.pickle', 'ab') as f:
# 				pickle.dump(dict(itertools.islice(merged_idx.items(), 50)), f)
# 				merged_idx = dict(itertools.islice(merged_idx.items(), 50, None))


# print(merged_idx)







# chunk_lst = list()
# total_idx = list()

# def merge_index(file_num):
# 	for i in range(0, file_num):
# 		with open('inv'+str(i)+'.pickle', 'rb') as f:
# 			chunk_lst.append(pickle.load(f))


# 	# Depth
# 	for j in range(0, 1):
# 		# Width
# 		for i in range(0, len(chunk_lst)):
# 			if next(iter(chunk_lst[i]) == next(iter(chun_lst[i+1]):
# 				if chunk_lst[i][j].key in total_idx:

# 					total_idx[chunk_lst[i][j].key].append(chunk_lst[i][j].values)
# 					total_idx[chunk_lst[i+1][j].key].append(chunk_lst[i+1][j].values)
# 				else:
# 					total_idx.append(chunk_lst[i][j])
# 					total_idx[chunk_lst[i+1][j].key].append(chunk_lst[i+1][j].values)

# 				chunk_lst[i].pop(chunk_lst[i][j].key)
# 				chunk_lst[i+1].pop(chunk_lst[i+1][j].key)

# 			i+=1


# merge_index(3)



# dct1 = {"a":[1,2], "b":[3], "e":[4]}
# dct2 = {"a":[3,8], "c":[9]}

# print(dict(itertools.islice(dct1.items(), )))

# chunk_lst = list([dct1])
# chunk_lst.append(dct2)

# merged_idx = dct1

# for key, value in dct2.items():

# 	if key in merged_idx:
# 		for val in value:
# 			merged_idx[key].append(val)
# 	else:
# 		merged_idx[key] = value

# print(merged_idx)




# lst = [1,2,3]

# print()


# print(list(chunk_lst[0].keys())[0])

# dct1.pop(list(chunk_lst[0].keys())[0])

# print(list(chunk_lst[0].keys())[0])


# print(chunk_lst)

# total_idx = {}

# # Depth
# for j in range(0, 2):
# 	# Width
# 	for i in range(0, len(chunk_lst)):

# 		key1 = list(chunk_lst[i].keys())[0]
# 		key2 = list(chunk_lst[i+1].keys())[0]

# 		val1 = list(chunk_lst[i].values())[0]
# 		val2 = list(chunk_lst[i+1].values())[0]

# 		if key1 == key2:
# 			if key1 in total_idx:
# 				total_idx[key1].append(val1)
# 				total_idx[key2].append(val2)
# 			else:
# 				total_idx[key1] = val1+val2
# 				# total_idx[chunk_lst[i+1][j].key].append(chunk_lst[i+1][j].values)

# 			chunk_lst[i].pop(key1)
# 			chunk_lst[i+1].pop(key2)

# 		elif key1 < key2:
# 			if key1 in total_idx:
# 				total_idx[key1].append(val1)
# 			else:
# 				total_idx[key1] = val1
# 				chunk_lst[i].pop(key1)

# 		else:
# 			if key2 in total_idx:
# 				total_idx[key2].append(val2)
# 			else:
# 				total_idx[key2] = val2
# 				chunk_lst[i+1].pop(key2)



# print(total_idx)


# chuk_lst = list()

# def iter_items(parser):
# 	for prefix, event, value in parser:
# 		if event == 'string':
# 			yield prefix, value

# def merge_index(file_num):

# 	for i in range(0, file_num):
# 		with open('inv'+str(i)+'.json', 'r') as f:
# 			items = iter_items(ijson.parser(f))
# 			print(dict(itertools.islice(items, 1)))
			
# with open('inv1.json', 'r') as f:
# 	# obj = ijson.items(f,"item")		
# 	# for o in obj:
# 	# 	print(str(o) + "\n")

# 	for o in ijson.items(f, ""):
# 		print(o)
# 		print("a")

# merge_index(1)


# json_data = []
# json_file = "inv0.json"

# file = open(json_file)
# for line in file:
# 	json_line = json.loads(line)
# 	print(json_line)
# 	print("\n")
# 	json_data.append(json_line)

# print(json_data)




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



