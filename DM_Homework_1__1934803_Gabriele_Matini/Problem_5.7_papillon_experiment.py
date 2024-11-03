import random
from collections import defaultdict
import itertools
#creates graph represented as tuple of tuples ((1,2), (1,4),(2,1),...) with completely ordered edges 
def create_graph(nodes):
	graph = []
	f_graph= []
	marked = [] #to not put the same edges more than once in the graph
	for i in nodes:
		for j in nodes:
			if i != j:
				choice = random.randint(0,1)
				k = [i,j]
				k.sort()
				if choice == 1:
					if not k in marked:
						
						graph.append(k)
						marked.append(k)
				else:
					marked.append(k)
	for i in graph:
		t = tuple(i)
		f_graph.append(t)
	
	f_graph.sort()
	f_graph = tuple(f_graph)
	return f_graph
#takes list of nodes and the graph 
def get_papillons(graph, nodes):
	nw_edges = {}
	for n in nodes:
		nw_edges[n] = []
	for e in graph:
		nw_edges[e[0]].append(e[1])
		nw_edges[e[1]].append(e[0])
	#get all possible "centers" of the papillon, aka those that have 4 edges and are the center of the papillon form (so these are nodes with at least 4 edges)
	candidate_centers = []
	for n in nw_edges.keys():
		if len(nw_edges[n]) >= 4:
			candidate_centers.append(n)
			
	papillons = []
	combinations = []
	for c in candidate_centers:
		#get all possible combinations of 4 edges
		#edges list for c = nw_edges[c]
		combinations = list(itertools.combinations(nw_edges[c], 4))
		for comb in combinations:
			#get all 15 papillons with this subset of len(comb)+1 nodes
			list_comb = list(comb)
			edges = list(itertools.combinations(nw_edges[c], 2)) #
			for e1 in edges:
				for e2 in edges:
					#take all couples of edges with no nodes in common
					if e1[0] != e2[0] and e1[0] != e2[1] and e1[1] != e2[0] and e1[1] != e2[1]:
						#now check if this combination is present in the graph
						if e1 in graph and e2 in graph:
							#now check that the no other edges between these 4 non center nodes are present, these are the 4 remaining edges
							w1 = [e1[0],e2[0]]
							w1.sort()
							w1 = tuple(w1)
							w2 = [e1[0],e2[1]]
							w2.sort()
							w2 = tuple(w2)
							w3 = [e1[1],e2[0]]
							w3.sort()
							w3 = tuple(w3)
							w4 = [e1[1],e2[1]]
							w4.sort()
							w4 = tuple(w4)
							if (not w1 in graph) and (not w2 in graph) and (not w3 in graph) and (not w4 in graph):
								#we found a papillon!
								pap = [[c,e1[0]], [c,e1[1]], [c,e2[0]], [c,e2[1]], [e1[0], e1[1]], [e2[0],e2[1]]]
								for p in pap:
									p.sort()
								pap.sort()
								papillon = []
								for p in pap:
									papillon.append(tuple(p))
								papillon.sort()
								papillon = tuple(papillon)
								if papillon not in papillons:
									papillons.append(papillon)
								
	return papillons
								
#try for n=6						
nodes = [1,2,3,4,5,6]
papillons = []
count = 0
for i in range(1, 1000000):
	
	g = create_graph(nodes)
	p = get_papillons(g, nodes)
	count += len(p)
	p.sort()
	p = tuple(p)
	for el in p:
		if el not in papillons:
			papillons.append(el)
print(f"Expected value for n=6 and p=1/2 is {count/1000000}")#expected value bruteforced with one-milion tries

print(f"For n=6, we have {len(papillons)} possible papillons")
#for n=6 they are 90
