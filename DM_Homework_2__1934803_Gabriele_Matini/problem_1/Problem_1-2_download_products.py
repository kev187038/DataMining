import urllib.request
from lxml import html
from time import sleep

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    return response.content

def parse_page(page, num, found_products):
    tree = html.fromstring(page)
    products = []
    #//tag[@attribute='value']/text() to select all texts of tags with that attribute value
    #Inspecting the page element on the site, all results are signed with data-component-type="s-search-result"
    #The title of the product is a h2/a/span path, while the url is in a h2/a/(href of a) path
    #The stars are revealed in a text inside a span text like this "4.6 su 5 stelle"
    #Price is in a class' "a-offscreen" text
    #Prime is present if the class "s-prime" or "a-icon-prime" is present, we use contains for that

    product_elements = tree.xpath('//div[@data-component-type="s-search-result"]')

    for item in product_elements:
    	title = item.xpath('.//h2/a/span/text()')
    	link = item.xpath('.//h2/a/@href')
    	stars = item.xpath('.//span[@class="a-icon-alt"]/text()')
    	price = item.xpath('.//span[@class="a-price"]/span[@class="a-offscreen"]/text()')
    	prime = item.xpath('.//span[contains(@class, "s-prime")]')
    	
    	if title and price and link and f"https://www.amazon.it{link[0]}" not in found_products: #avoid storing duplicates
            products.append({
            	"id" : num,
                "description": title[0].strip(),
                "price": price[0].strip().replace('\xa0',""), #remove \xa0 char otherwise we get price strings like 299.99\xa0$
                "prime": bool(prime),
                "url": f"https://www.amazon.it{link[0]}",
                "stars": stars[0].strip().split()[0] if stars else None
            })
            num += 1
            found_products.append(f"https://www.amazon.it{link[0]}")

    return (products, num, found_products)
    
	

site = "https://www.amazon.it/"
keyword = "computer"
max_pages = 7 #we get seven pages of results in total, searching the page on the browser on amazon.it/keyword=computer, these are all the pages
products = []
found = []
page = 1
num = 1
with open('products.tsv', 'a', encoding='utf-8') as f:
	f.write("Id\tDescription\tPrice\tPrime\tURL\tStars\n")
	while page <= max_pages:  
		url = f"{site}s?k={keyword}&page={page}"
		#send request and get response to parse
		with urllib.request.urlopen(url) as response:
	   		response = response.read()
	   		products, num, found = parse_page(response, num, found)
	   		for product in products:
	   			print(f"{product['id']}\t{product['description']}\t{product['price']}\t{product['prime']}\t{product['url']}\t{product['stars']}\n")
	   			f.write(f"{product['id']}\t{product['description']}\t{product['price']}\t{product['prime']}\t{product['url']}\t{product['stars']}\n")
	   				
	   		sleep(90)
		page+=1
