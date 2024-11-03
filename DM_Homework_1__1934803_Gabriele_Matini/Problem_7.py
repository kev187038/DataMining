from collections import defaultdict
#Among beers with at least 100 reviews find top 10 beers with highest average review score
#Beers with their scores
beers = defaultdict(int)
#Beers with their review count
beer_counts = defaultdict(int)
sorted_dict = None
with open('./beers.txt', 'r') as f:

	line = f.readline().strip().split('\t')
	
	while(line != ['']):
	
		beer_counts[line[0]] += 1
		beers[line[0]] += int(line[1])
		line = f.readline().strip().split('\t')
	
	for beer in list(beers.keys()):
		#Remove all beers with less than 100 reviews
		if beer_counts[beer] < 100:
			v = beers.pop(beer)
			v = beer_counts.pop(beer)
				
		#Get beers' averages
		else:
			beers[beer] = beers[beer] / beer_counts[beer]
	
	sorted_dict = dict(sorted(beers.items(), key= lambda item: item[1], reverse=True))
	
	#Finally, write results on a file
	top_10 = list(sorted_dict.items())[:10]
	with open('./Problem_7_script_results.txt','a') as res:
		res.write('Beer\tAverage Score\n')
		for el in top_10:
			res.write(el[0] + '\t' + str(el[1]) + '\n')
