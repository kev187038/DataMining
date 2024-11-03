import random
#First four cards at least 1 club
def ex_a(deck):
	draw = deck[:4]
	if any(card.endswith('Clubs') for card in draw):
		return 1
	else:
	 return 0
#First seven cards include exactly one club
def ex_b(deck):
	draw = deck[:7]
	c = 0
	for card in draw:
		if card.endswith('Clubs'):
			c += 1
		if c > 1:
			return 0
	if c == 0:
		return 0
	else:
		return 1
#First three cards all of same suit
def ex_c(deck):
	draw = deck[:3]
	suit = draw[0].split()[-1]
	if all(card.endswith(suit) for card in draw[1:]):
		return 1
	else:
		return 0
#First three cards all sevens
def ex_d(deck):
	draw = deck[:3]
	if all(card.startswith('7') for card in draw):
		return 1
	else:
		return 0
#First five cards form a straight
def ex_e(deck):
	draw = deck[:5]
	#Check if cards are same suit to remove full straight
	suit = draw[0].split()[-1]
	if all(card.endswith(suit) for card in draw[1:]):
		return 0
	#Check cards form any straight
	straights = ['12345', '23456', '34567', '45678', '56789', '678910', '7891011', '89101112', '910111213', '110111213']
	numbers = [card.split()[0] for card in draw]
	for i in range(len(numbers)):
		if numbers[i] == 'Ace':
			numbers[i] = 1
		elif numbers[i] == 'Jack':
			numbers[i] = 11
		elif numbers[i] == 'Queen':
			numbers[i] = 12
		elif numbers[i] == 'King':
			numbers[i] = 13
		else:
			numbers[i] = int(numbers[i])
	numbers.sort()
	s = ''
	for i in numbers:
		s += str(i)
	
	if s in straights:
		return 1
	else:
		return 0
	
	

def simulate_draws(num_simulations, exercise):
    
    successes = 0
    
    for _ in range(num_simulations):
        deck = ['Ace of Hearts', 'Ace of Diamonds', 'Ace of Clubs', 'Ace of Spades'] + \
               [f'{rank} of {suit}' for rank in range(2, 11) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']] + \
               ['Jack of Hearts', 'Jack of Diamonds', 'Jack of Clubs', 'Jack of Spades', 
                'Queen of Hearts', 'Queen of Diamonds', 'Queen of Clubs', 'Queen of Spades', 
                'King of Hearts', 'King of Diamonds', 'King of Clubs', 'King of Spades']

        random.shuffle(deck)
        if exercise == 'a':
        	successes += ex_a(deck)
        elif exercise == 'b':
        	successes += ex_b(deck)
        elif exercise == 'c':
        	successes += ex_c(deck)
        elif exercise == 'd':
        	successes += ex_d(deck)
        elif exercise == 'e':
        	successes += ex_e(deck)

  
    probability = successes / num_simulations
    return probability


num_simulations = 1000000
exercises = ['a', 'b', 'c', 'd', 'e']
print(f"Starting simulation that uses {num_simulations} draws to test all exercises...")
for e in exercises:
	prob = simulate_draws(num_simulations, e)
	res = f'Calculated probability of exercise {e}: {prob:.6f}'
	print(res)
	with open('Problem_1_script_results.txt','a') as f:
		f.write(res + '\n')

