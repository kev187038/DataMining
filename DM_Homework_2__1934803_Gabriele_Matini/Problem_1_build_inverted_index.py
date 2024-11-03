import nltk
import re
from collections import defaultdict
#We build an inverted index and store it into a file.
nltk.download('stopwords')

#We normalize, then remove punctuation and stopwords from the description
def preprocess(desc):
	
	#Normalize
	desc = desc.lower() 
	
	#Tokenize and remove punctuation
	tokenizer = nltk.tokenize.RegexpTokenizer(r'[\w-]+(?:[\d-]*[\.,]*[\d-]+)*') #do not remove numbers in the form 1.5 or 1,5, also we want expressions like wi-fi, ddram-4 4,5-5 to be available
	#print(desc)
	tokens = tokenizer.tokenize(desc)
	#Remove stopwords
	stop_words = set(nltk.corpus.stopwords.words('italian'))
	f_tokens = [token for token in tokens if token not in stop_words and token != '-']
	#print(f_tokens)
	return f_tokens
	
inverted_index = defaultdict()

#Retrieve data from the products.tsv file
with open("products.tsv","r") as f:
	l = f.readline(); #l[1] = desc, l[2] = price, l[3] = prime, l[4] = link, l[5] = rating
	
	while l != ['']:
		l = f.readline().strip().split("\t")
		id_ = l[0]
		desc = preprocess(l[1])
		for word in desc:
			inverted_index[word].append(id_)
	print(desc)
