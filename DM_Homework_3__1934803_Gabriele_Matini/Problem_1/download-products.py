import urllib.request
from lxml import html
from time import sleep
import random
#Download script to download more pages: this time we want more pages and to expand the dataset
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
    	
    	if title and price and link and title[0].strip() not in found_products: #avoid storing duplicates, this time we don't want
            products.append({
            	"id" : num,
                "description": title[0].strip(),
                "price": price[0].strip().replace('\xa0',""), #remove \xa0 char otherwise we get price strings like 299.99\xa0$
                "prime": bool(prime),
                "url": f"https://www.amazon.it{link[0]}",
                "stars": stars[0].strip().split()[0] if stars else None
            })
            num += 1
            found_products.append(title[0].strip())

    return (products, num, found_products)
    
	

site = "https://www.amazon.it/"
keyword = "computer"
products = []
found = []
num = 1

#Keep dowloading until the number of consecutive pages getting only duplicates surpasses 10
with open('products.tsv', 'w', encoding='utf-8') as f:
	f.write("Id\tDescription\tPrice\tPrime\tURL\tStars\n")
	page = 1
	duplicate_pages = 0
	while duplicate_pages <= 10:  
		url = f"{site}s?k={keyword}&page={page}"
		req = urllib.request.Request(
		    url,
		    headers={
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
		    }
		)
		#send request and get response to parse
		with urllib.request.urlopen(req) as response:
	   		response = response.read()
	   		products, num, found = parse_page(response, num, found)
	   		for product in products:
	   			print(f"{product['id']}\t{product['description']}\t{product['price']}\t{product['prime']}\t{product['url']}\t{product['stars']}\n")
	   			f.write(f"{product['id']}\t{product['description']}\t{product['price']}\t{product['prime']}\t{product['url']}\t{product['stars']}\n")
	   		if products == []:
	   			duplicate_pages += 1
	   			print(duplicate_pages)
	   		else:
	   			duplicate_pages = 0
	   		print(f"Current page is {page}")
	   		sleep(1)
		page+=1

print(f"Pages visited were {page}")
print("Finished!")
