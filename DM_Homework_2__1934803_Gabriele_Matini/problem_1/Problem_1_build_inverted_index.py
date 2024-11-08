import nltk
import re
import json
import math

nltk.download('stopwords')
products = []
#We normalize, then remove punctuation and stopwords from the description
#We do not remove numbers in the form 1.5 or 1,5, also we want expressions like wi-fi, ddram-4 4,5-5 to be available.
def preprocess(desc):
	
	#Normalize
	desc = desc.lower() 
	
	#Tokenize and remove punctuation
	tokenizer = nltk.tokenize.RegexpTokenizer(r'[\w]+(?:\.[\w-]+)*') 
	tokens = tokenizer.tokenize(desc)
	stop_words = set(nltk.corpus.stopwords.words('italian'))
	f_tokens = [token for token in tokens if token not in stop_words and token != '-']
	return f_tokens

	
inverted_index = {}

#Retrieve data from the products.tsv file
with open("products.tsv","r") as f:
	l = f.readline(); #l[1] = desc, l[2] = price, l[3] = prime, l[4] = link, l[5] = rating
	l = f.readline().strip().split("\t")
	while l != ['']:
		id_ = l[0]
		products.append({'description' : l[1], 'price': l[2], 'prime':l[3], 'link':l[4], 'rating':l[5]})
		desc = preprocess(l[1])
		for word in desc:
			if  word not in inverted_index.keys():
				inverted_index[word] = []
			inverted_index[word].append(id_)
		l = f.readline().strip().split("\t")

#Save inverted index
with open("inverted_index.json", "w", encoding='utf-8') as idx:
	json.dump(inverted_index, idx)

#Build tf-idf 

#Need term frequency of words in a doc * log(N_descriptions/N_descriptions_in_which_word_wi_appears)
N_desc = len(products)
tf = {}  

#Build tf
for word, desc_ids in inverted_index.items():
    for desc_id in desc_ids:
        if desc_id not in tf:
            tf[desc_id] = {}
        tf[desc_id][word] = tf[desc_id].get(word, 0) + 1  
        
#Build idf   idf = log(N_descriptions/N_descriptions_in_which_word_wi_appears)
N_desc = len(products)
idf = {}
for word in inverted_index.keys():
    idf[word] = math.log(N_desc / len(inverted_index[word]))/math.log(10)

#Create tf-idf
tfidf = {}
for desc_id, terms in tf.items():
    tfidf[desc_id] = {}
    for word, term_freq in terms.items():
        tfidf[desc_id][word] = term_freq * idf[word]  
        
#Save tdf-idf
with open("tdf_idf_problem_1.json","w") as f:
	json.dump(tfidf, f)

