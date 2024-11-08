import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import math
import nltk
def preprocess(desc):
	desc = desc.lower() 
	tokenizer = nltk.tokenize.RegexpTokenizer(r'[\w]+(?:\.[\w-]+)*') #do not remove numbers in the form 1.5 or 1,5, also we want expressions like wi-fi, ddram-4 4,5-5 to be available
	tokens = tokenizer.tokenize(desc)
	stop_words = set(nltk.corpus.stopwords.words('italian'))
	f_tokens = [token for token in tokens if token not in stop_words and token != '-']
	return f_tokens
	

#Query is the input query, tfidf is the tfidf values retrieved for vector product construction, len_vec is the length of the vectors (number of products), inv_idx is inverted index
def calculate_cosine_similarity(query, tfidf, len_vec, inv_idx, num_products):
	query_terms = preprocess(query)
	words = list(inv_idx.keys())
	words.sort()
	query_tf = {term: query_terms.count(term) for term in query_terms}
	query_vector = np.zeros(len_vec)  
	
	# Build query vector
	for idx, word in enumerate(words):
		if word in query_tf:
			idf = math.log(num_products / len(inv_idx[word]))/math.log(10)
			query_vector[idx] = query_tf[word] * idf
	
	#Build description vectors
	descriptions = list(tfidf.keys())
	for i in range(len(descriptions)):
		descriptions[i] = int(descriptions[i])
	descriptions.sort()

	desc_vectors = [] #list position is the desc_id relative to the vector
	for desc_id in descriptions:
		desc_vector = np.zeros(len_vec)
		for idx, word in enumerate(words):
			desc_vector[idx] = tfidf[str(desc_id)].get(word, 0)
		desc_vectors.append(desc_vector)

	desc_vectors = np.array(desc_vectors)
	#Do cosine similarity
	similarities = cosine_similarity([query_vector], desc_vectors)[0]
	return similarities


#Retrieve resources
tfidf = {}
with open('tdf_idf_problem_1.json', 'r') as f:
	tfidf = json.load(f)

len_vec = 0
inv_idx = {}
with open('inverted_index.json', 'r') as f:
	inv_idx = json.load(f)
	len_vec = len(inv_idx.keys())
	
while True:

	products = {}
	with open("products.tsv","r") as f:
		l = f.readline()
		l = f.readline().strip().split('\t')
		while l != ['']:
			products[l[0]] = {'description' : l[1], 'price': l[2], 'prime':l[3], 'link':l[4], 'rating':l[5]}
			l = f.readline().strip().split('\t')
        #Ask the user for their query
	query = input("Insert your query(to exit press enter without insering anything): ")
	if query == '':
        	break

	similarities = calculate_cosine_similarity(query, tfidf, len_vec, inv_idx, len(products))

	#Return results in order of cosine similarity with description
	results = []

	for i in range(len(similarities)):
		
		results.append((similarities[i], i+1))

	results.sort(reverse=True)
	print(f"Inputted query is: {query}")
	print("Results in order of similarity are:")
	i = 0
	while i < len(products):
		print("\n")
		print(f"Sim_value: {round(results[i][0], 5)},\n{products[str(results[i][1])]['description']},\n Price: {products[str(results[i][1])]['price']},\n Prime: {products[str(results[i][1])]['prime']},\nLink: {products[str(results[i][1])]['link']},\nRating: {products[str(results[i][1])]['rating']}")
		i += 1


