import requests
from requests.exceptions import MissingSchema
from bs4 import BeautifulSoup as BFS
import random
import datetime
import json

class craigslistScan:
    def __init__(self):
        ## CRAIGSLIST FREE / PAYED
        self.craigslist = "https://sandiego.craigslist.org/search/ssd/sss"

        self.products = []

        self.headers_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)"
        ]
        self.headers = {"User-Agent": random.choice(self.headers_list)}
        #self.ebay = open("", "r")


    """
        THIS WHOLE CLASS GOES IN A CHAIN OF EVENTS

        FIRST IS DISPLAY THE PROCUTS
        NEXT IS ENHANCE
        LAST IS WRITE TO THE FILE
    """

    # display all the products on the page
    def displayProducts(self):
        site = requests.get(self.craigslist, headers=self.headers)
        link_list = []

        # Get all the links
        soup = BFS(site.text, 'html.parser')
        links = soup.find_all("a", href=True)
        for a in links:
            link_list.append(a['href'])

        
         # get rid of the weird # and / in the beginning of  the list
        link_list = [link for link in link_list if link not in ["/", "#"]]
        
        self.enhanceProducts(link_list) # enhance the products (open it up on another requests bitchass thing idfk)


    def enhanceProducts(self, product): # enhance the product on another page
        for link in product:
            full_url = f"{self.base_url}{link}" if link.startswith("/") else link
            site = requests.get(full_url, headers=self.headers)
            

            if site.status_code == 200:
                soup = BFS(site.text, 'html.parser')

                try:
                    # find the price
                    p = soup.find(
                        "span", 
                        {
                        "class" : "price"
                        })
                    
                    p_text = p.get_text(strip=True) if p else "N/A"
                    
                    # find the title
                    title = soup.find(
                        "span",
                        {
                            "id": "titletextonly"
                        }
                        )
                    
                    title_text = title.get_text(strip=True) if title else "N/A"

                    # get the description
                    desc = soup.find(
                        "section",
                        {
                            "id": "postingbody"
                        }
                    )
                    desc_text = desc.get_text(strip=True) if desc else "N/A"
                    

                    # write all the data found in a dictionary
                    product_info = {
                        "link": link,
                        "title": title_text,
                        "description": desc_text,
                        "price": p_text
                    }
                    self.products.append(product_info)
                
                except Exception as e:
                    print(e)
        self.writeToFile()

    # write to the file
    def writeToFile(self):
        print(f"Writing {len(self.products)} products to file") # declare shit is being written

        if not self.products: # detect if no products were found
            print("No products found to write!")
            return
            
        final = json.dumps(self.products, indent=4) # dump the data into json format
        with open("json/craigsListProducts.json", "w", encoding="utf-8") as j: # open the file
            j.write(final)

        print("Products saved to products.json") # final message
        print(datetime.datetime.now())



class cleanUpCraigslistData:
    def __init__(self):
        # clean up the description by removing this one fucking phrase
        self.uselessPhrases = 'QR Code Link to This Post'
    
    def clean_up_description(self): # description has this weird
        # Load the JSON data
        with open("json/craigsListProducts.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        # Ensure data is a list
        if isinstance(data, list):
            for item in data:
                if "description" in item and isinstance(item["description"], str):
                    for phrase in self.uselessPhrases:
                        item["description"] = item["description"].replace(phrase, "").strip()

        # Save the cleaned data back to the JSON file
        with open("json/craigsListProducts.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)



"""
    IN THIS SECTION I WANT TO SIMPLIFY THE TITLE ENOUGH SO THAT EBAY CAN PARSE WHAT I AM TRYING TO LOOK FOR

    TODO: feed the simplified title back into the ebay queryer
"""
class simplifyTitle:
    def __init__(self): # define the variables

        """
            SET THE STOP WORDS IN stopwords-en.txt AS A VARIABLE TO PARSE THROUGHT
        """
        with open("simplify text words/stopwords-en.txt", "r", encoding='utf-8')as a: 
            r_ = a.read()


        self.n = r_.splitlines() # split the text into an array to parse throught

        # define useless characters such as numbers, punctuation and etc
        self.punctuation = "!#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    
    # finally simplify the title
    def title_simplify(self):
        # Load existing data
        with open('json/craigsListProducts.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Process each product
        for item in data:
            if "title" in item and isinstance(item["title"], str):
                # Convert title to lowercase
                title_lower = item["title"].lower()

                # Split into words
                words = title_lower.split()

                # Remove stopwords and punctuation
                filtered_words = []
                for word in words:
                    if word not in self.n and word not in self.punctuation:
                        filtered_words.append(word)

                # Join words with '+' for the eBay search query
                simplified_title = "+".join(filtered_words)

                # Add the simplified title to the product data
                item["simplified_title"] = simplified_title

        # Save the modified data back to the JSON file
        with open("json/craigsListProducts.json", "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

def main():
    # webscrape section
    w = craigslistScan()
    w.displayProducts()

    # IN THE START OF THE DESCRIPTION THERE IS THIS WEIRD "QR Code Link to This Post" THAT I AM REMOVING WITH THIS SECTION FO CODE
    clean = cleanUpCraigslistData()
    clean.clean_up_description()

    # IN THIS SECTION IS WHERE I WANT TO MAKE A SIMPLIFIED TITLE SO I CAN QUERY IT INTO EBAY
    s = simplifyTitle()
    s.title_simplify()

main()