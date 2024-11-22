from utilities import Shingling, MinHashing, LSH, NNSearch
from time import time
products = []
#Extract all the descriptions from products.tsv and put them in a list with their Id (doc_id)
with open("./products.tsv","r") as f:
	l = f.readline(); #l[1] = desc
	l = f.readline().strip().split("\t")
	while l != ['']:
		products.append(l[1])
		l = f.readline().strip().split("\t")


#Problem parameters
k = 10 #shingle length
t = 0.8 #threshold
b = 50 #num bands
r = 20 #num rows
n = r*b #num hash functions

#Define classes
shingling = Shingling(k)
minhashing = MinHashing(n)
lsh = LSH(b,r)

shingle_sets = []
for p in products:
	shingles = shingling.create_shingles(p)
	shingle_sets.append(shingles)
nnsearch = NNSearch(shingle_sets)

#Implement LSH pipeline
start = time()
hashed_shingle_sets = []
for s in shingle_sets:
	hashed_shingle = shingling.hash_shingles(s)
	hashed_shingle_sets.append(hashed_shingle)
	
signatures = []
for e in hashed_shingle_sets:
	signatures.append(minhashing.compute_signature(e))

lsh_pairs = lsh.find_pairs(signatures, t)
end = time()
time1 = end-start
print(f"Elapsed time is {end-start}")
print(f"Pairs found by LSH are: {lsh_pairs}, \n they are {len(lsh_pairs)} pairs in total")
print(len(lsh_pairs))

start = time()
nn = nnsearch.find_nn(t)
end = time()
time2 = end-start
print(f"Elapsed time is {end-start}")
print(f"Real nn pairs are: {nn}, \nthey are {len(nn)} pairs in total")
print(f"Errors are: {lsh_pairs.union(nn) - lsh_pairs.intersection(nn)}")

for i in nn:
	print(products[i[0]] + "\n"+ products[i[1]]+ "\n\n")
	
#Write results
with open(f"./results_b={b}_r={r}_n={n}.txt","w") as f:
	f.write(f"Near duplicates found with LSH are: \n {lsh_pairs}, \n for a total of {len(lsh_pairs)} near duplicates. \n")
	f.write(f"\nTrue Nearest Neighbours are: \n {nn}, \n for a total of {len(nn)} duplicates. \n")
	f.write(f"\nErrors (both false positvies and false negatives) are: {lsh_pairs.union(nn) - lsh_pairs.intersection(nn)}.\n")
	f.write(f"\nThe intersection between the two results is {nn.intersection(lsh_pairs)} for a size of {len(nn.intersection(lsh_pairs))}.\n")
	f.write(f"\nThe time required for LSH was {time1} sec\n The time required to bruteforce the nearest neighbours was {time2} sec.")
	
	
	
	
	
	
	
	
