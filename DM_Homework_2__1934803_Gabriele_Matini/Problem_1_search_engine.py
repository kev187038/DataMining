import json
#from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import math
import nltk
def preprocess(desc):
	desc = desc.lower() 
	tokenizer = nltk.tokenize.RegexpTokenizer(r'[\w-]+(?:[\d-]*[\.,]*[\d-]+)*') #do not remove numbers in the form 1.5 or 1,5, also we want expressions like wi-fi, ddram-4 4,5-5 to be available
	tokens = tokenizer.tokenize(desc)
	stop_words = set(nltk.corpus.stopwords.words('italian'))
	f_tokens = [token for token in tokens if token not in stop_words and token != '-']
	return f_tokens
	


def calculate_cosine_similarity(query, tfidf, len_vec, inv_idx):
	query_terms = preprocess(query)
	words = list(inv_idx.keys())
	words.sort()
	query_tf = {term: query_terms.count(term) for term in query_terms}
	query_vector = np.zeros(len_vec)  
	# Build query vector
	for idx, word in enumerate(words):
		if word in query_tf:
			idf = math.log(len_vec / len(inv_idx[word]))
			query_vector[idx] = query_tf[word] * idf


	# Build description vectors
	desc_vectors = []
	for desc_id in tfidf.keys():
		desc_vector = np.zeros(len_vec)
		for idx, word in enumerate(words):
			desc_vector[idx] = tfidf[desc_id].get(word, 0)
		desc_vectors.append(desc_vector)
	print(desc_vectors)
	desc_vectors = np.array(desc_vectors)
	
	#Do cosine similarity
	similarities = cosine_similarity([query_vector], desc_vectors)[0]
	return similarities



tfidf = {}
with open('tdfidf_problem_1.json', 'r') as f:
	tfidf = json.load(f)
len_vec = 0
inv_idx = {}
with open('inverted_index.json', 'r') as f:
	inv_idx = json.load(f)
	len_vec = len(inv_idx.keys())
	

query = "computer lenovo pc"
similarities = calculate_cosine_similarity(query, tfidf, len_vec, inv_idx)

