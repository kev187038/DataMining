import hashlib
from collections import defaultdict

def hashFamily(i):
      #Use the suggested hash functions generating function
      resultSize = 8 # how many bytes we want back
      maxLen = 20 # how long can our i be (in decimal)
      salt = str(i).zfill(maxLen)[-maxLen:].encode('utf-8')
      def hashMember(x):
          return int.from_bytes(hashlib.sha1(x + salt).digest()[-resultSize:], 'big') #we use numerical representation of shingles and signatures
      return hashMember

#Implement pipeline Shingling -> MinHashing -> LSH -> Output

class Shingling:

    def __init__(self, k):
        self.k = k#shingle length

    #Input: string document - Output: Shingles
    def create_shingles(self, document):

        shingles = []
        
        #Handle case in which len(document) < length of shingle, so we use the entire document as a single shingle here.
        if len(document) < self.k:
            shingles.append(document)
        else:
            for i in range(len(document) - self.k + 1):
                shingles.append(document[i:i + self.k])
        shingles.sort()
        return shingles

    #Input: list of shingles - Output: hashed shingles, for some hash function
    def hash_shingles(self, shingles):
        #Use a specific hash function for all shingles
        hash_function = hashFamily(0)
        hashed_shingles = []
        for shingle in shingles:
            hashed_shingles.append(hash_function(shingle.encode('utf-8')))
        return hashed_shingles


class MinHashing:

    def __init__(self, num_hash_functions, max_hash_value=None):
        
        self.num_hash_functions = num_hash_functions
        self.max_hash_value = max_hash_value if max_hash_value else 2**32 - 1
        self.hash_functions = [hashFamily(i) for i in range(num_hash_functions)] 

    #Input: set of hashed shingles - Output: signature list
    def compute_signature(self, hashed_shingles):

        signature = []
        #Apply each hash function to the hashed shingles and find the minimum hash value
        for hash_function in self.hash_functions:
            min_hash = min(hash_function(shingle.to_bytes((shingle.bit_length() + 7) // 8, 'big')) for shingle in hashed_shingles) #calculate byte lenght of shingles rounding down
            signature.append(min_hash)
        return signature
        

class LSH:
    def __init__(self, num_bands, rows_per_band):
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.hash_functions = [hashFamily(i) for i in range(num_bands)]

    def hash_band(self, band, band_idx):
        #Break up the tuple of rows of the band into strings and return the hashed band
        band_str = ",".join(map(str, band)) 
        return self.hash_functions[band_idx](band_str.encode('utf-8'))

    #Input : signature list - Output: set of nearest neighbours tuples
    def find_pairs(self, signatures, threshold):
        #Find candidate pairs by hashing the bands and going through the buckets
        if not signatures:
            return set() 
        
        #Control that the numbers are correct
        assert len(signatures[0]) == self.num_bands * self.rows_per_band, \
            "The number of rows in a signature must equal num_bands * rows_per_band."

        #Create hash buckets for each band
        buckets = [defaultdict(list) for i in range(self.num_bands)] #create list of num_bands buckets

        #Divide signatures into bands and hash them
        for doc_id, signature in enumerate(signatures):
            for band_idx in range(self.num_bands):
                start = band_idx * self.rows_per_band
                end = start + self.rows_per_band
                band = tuple(signature[start:end]) #get single bands of signature as tuples
                bucket = self.hash_band(band, band_idx)
                buckets[band_idx][bucket].append(doc_id) #add doc_id to the bucket


        #Find candidate pairs in the bucket lists inside each band_idx set of lists
        candidate_pairs = set()
        for band_buckets in buckets:
            for bucket_docs in band_buckets.values():
                if len(bucket_docs) > 1:
                    #print(cv, bucket_docs)
                    #Add all pairs of documents in the same bucket
                    for i in range(len(bucket_docs)):
                        for j in range(i + 1, len(bucket_docs)): #need to put all docs inside candidate pairs without putting the pair containing the same doc
                            candidate_pairs.add((bucket_docs[i], bucket_docs[j]))
        
        return candidate_pairs
        

#Testing class: given shingles of a set of docs, it finds nearest neighbours with naive, bruteforce implementation
class NNSearch:
    def __init__(self, shingles):
        self.shingles = {}
        for doc_id, shingle_set in enumerate(shingles):
            self.shingles[doc_id] = set(shingle_set)
  
    #Input: sets of shingles - Output: nearest neighbours
    def find_nn(self, threshold):
    	#Find intersection between shingles sets
    	num_docs = len(self.shingles.keys())
    	nearest_neighbours = set()
    	
    	print("Real calculated similarities of true NN were:")
    	for i in range(num_docs):
    	    for j in range(i + 1, num_docs):
    	        #For each docs, calculate Jaccard similarity and see if it surpasses the threshold
    	        size_intersection = len(self.shingles[i].intersection(self.shingles[j]))
    	        size_union = len(self.shingles[i].union(self.shingles[j]))
    	        sim = size_intersection / size_union
    	        if sim >= threshold:
    	            print(f"Bruteforced sim of {(i, j)} is: {sim}")
    	            nearest_neighbours.add((i,j))

    	return nearest_neighbours
    	
