import random
c = 0
s = 0
N = 1000000 #number of experiments
numpages = 10 
for i in range(N):
	a = random.randint(1,numpages)
	g = random.randint(1,numpages)
	while a == g:
		a = random.randint(1,numpages)
		g = random.randint(1,numpages)
	x = random.randint(1,numpages)
	
	#Uncomment these two lines to remove the possibility of equality, giving us always probability of 2/3 no matter the "numpages" number
	#while(x==a or x==g):
	#	x = random.randint(1,numpages)
		

	choice = random.randint(0,1)
	#Choose Aris
	if choice == 0:
		if x < a:
		#If Aris tells us a higher number than x, choose G < A
			s += int(g<a)
		else:
		#Else pick A as smallest
			s += int(g>a)
	#Same reasoning for Gianluca
	elif choice == 1:
		if x < g:
			s += int(g>a)
		else:
			s += int(g<a)
		
	
		

print(f'Probability is: {s/N}')
