"""

TODO: Finish the ebay scanner and make sure the images match the actual product. 

"""

import requests
from bs4 import BeautifulSoup
import numpy
import json
import time
import os
import datetime

class ParseSearchBar:
    """
        the goal is to use the search query method in ebay

        I want to be able to search a keyword based on the craigslist findings
    """


    def __init__(self):
        self.return_parsed_products = []
    
    def send_req(self, search_title):
        """
            Parse the tag given so that ebay can read it correctly
        """
        site = f"https://www.ebay.com/sch/i.html?_nkw={search_title}&_sacat=0&_from=R40&_trksid=p4432023.m570.l1313" # put the parsed title within the link

        html_content = requests.get(site).text # send the request, along with getting the html content of the page
        return html_content # return the content


    """
        Parse the content on the ebay website
    """
    def read_ebay(self, content):
        # have beautiful sup parse the data
        soup = BeautifulSoup(content, "html.parser")

        pre = soup.prettify() # make the shit not look like diarrhea 


        title_ = soup.find_all(class_="s-item__title")

        price_ = soup.find_all(class_="s-item__price")

        link_ = soup.find_all(
            'a', 
            class_='s-item__link', 
            href=True
            )
        
        img_ = soup.find_all('img')

        for title, price, link, img in zip(title_, price_, link_, img_): # Beautiful soup returns as a list, so you have to parse through the whole damn things. That or I am fucking doing it wrong.
            product_name = title.get_text(strip=True)
            product_price = price.get_text(strip=True)
            product_link = link['href']
            product_img = img['src']

            if product_name == "Shop on eBay":
                img_.remove(img)

            else:
                d = {
                    "product": product_name,
                    "price": product_price,
                    "link": product_link,
                    "img_src": product_img
                }
                self.return_parsed_products.append(d)


    # write to a json file and compare prices
    def return_file(self):
        with open("json/ebayProducts.json", "w", encoding="utf-8")as json_file:
            json.dump(self.return_parsed_products, json_file, indent=4)

class analyzeData:
    """
        TODO:

            1): Get an average price of product
            2): Compare it with what it is being sold for on craigslist
            3): Calculate the margin
            4): Look at the demand through AI
            5): Append all the data to a new json file


        ################################################################
            
            HOW THE JSON FILE WILL LOOK
            {
                "product": EBAY_LINK,
                "average_price": CALCULATED_AVERAGE,
                "craigslist_listing": CRAIGSLIST_PRICE,
                "market_demand": DEMAND
            }


            Flow chart of the functions:
                1): getAveragePrice() -> removeOutliers() -> compare()
                2): compare() -> calculateMargin() -> writeToJsonFile()
                3): writeToJsonFile() -> write to json file ##COMPLETED JSON FILE WITH PRODUCTS
    """

    def __init__(self, craigs, p):
        self.product = ''
        self.craigslist_listing = 0
        self.market_demand = 0
        self.file = []
        self.craigslistFile = []
        self.average = 0
        self.craigslist = craigs
        self.product = p

        self.margin = 0
        self.lowest = 0
        self.maximum = 0
        self.finalProduct = []

        # define the json file as an object within this class


        """
            EBAY PRODUCT
        """
        try:
            # Ebay product
            with open('json/ebayProducts.json', 'r', encoding='utf-8')as f:
                self.file = json.load(f)

            # craigslist product
            with open('json/craigsListProducts.json', 'r', encoding='utf-8')as file:
                self.craigslistFile = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            print('error: Could not load JSON file.')



    def removeOutliers(self, k=1.5):
        data = []
        for obj in self.file:
            try:
                num = float(obj['price'].replace('$', '').replace(',', ''))  # Handle commas in prices
                data.append(num)
            except ValueError:
                continue  # Skip invalid price formats
    
        data = numpy.array(data)  # Convert list to NumPy array

        q1 = numpy.percentile(data, 25)
        q3 = numpy.percentile(data, 75)
        iqr = q3 - q1
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr

        filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]  # Now works correctly
        return filtered_data
    

    def getAveragePrice(self):
        fixed = self.removeOutliers()

        self.average = numpy.mean(fixed)
        self.lowest = min(fixed)
        self.maximum = max(fixed)



        # do a check to makme sure there is a product for everything
        if self.craigslist != "N/A":
            print(f'PRODUCT: {self.product} \n AVERAGE: {self.average} \n MIN: {self.lowest} \n MAX: {self.maximum} \n CRAIGSLIST_LISTING: {self.craigslist} \n')
        else:
            pass

    def compare(self): # check if it is above or below the average. If above do not sell, if below calculate the best amount of margin
        if self.craigslist == 'N/A':
            pass
        else:
            c_price = float(self.craigslist.replace('$', '').replace(',', ''))

            if c_price > self.average:
                print('NOT A GOOD PRODUCT\n \n')
            else:
                print('GOOD PRODUCT\n\n')
                self.calculateMargin()



    def calculateMargin(self): # used to calculate the margin 
        """
            IN THIS SECTION I WANT TO FIND A GOOD PRICE

            I am planning on using simple math to make that work


            The calculations for margin are this ((price - cost) / price) * 100
        """
        if self.craigslist == 'N/A':
            pass
        else:
            c_price = float(self.craigslist.replace('$', '')) # THE COST
            self.margin = ((self.average - c_price) / c_price) * 100

            print(f'MARGIN: {self.margin} \n\n')

        dict = {
            "product": self.product,
            "average_price": self.average,
            "craigslist_listing": self.craigslist,
            "margin": self.margin
        }

        self.finalProduct.append(dict)
        

    def writeToJsonFile(self):
        with open("json/finalProduct.json", "a", encoding="utf-8")as json_file:
            json.dump(self.finalProduct, json_file, indent=4)

def main():
    # WEB SCRAPING SECTION
    
    # open the simplified shiz
    with open('json/craigsListProducts.json', 'r', encoding='utf-8')as f:
        data = json.load(f)

    # define the object for webscraping
    p = ParseSearchBar()


    """
        PRICE AVERAGE STARTS HERE
    """
    # define the class


    # loop to constantly find products
    for a in data:
        """
            THIS SECTION GETS THE DATA FROM THE CRAIGSLIST JSON FILES.
        """
        parsed_link = a['simplified_title']
        price_craigslist = a['price']
        # put the request link into a variable to get the data from said website
        req = p.send_req(parsed_link)
        
        # read the fucking ebay content
        read = p.read_ebay(req)
        # return the data to a json file
        p.return_file()
    
        """
            THIS SECTION IS MEANT TO ANALYZE THE PRICES AND DETERMINE WHICH PRODUCTS ARE A GO
        """
        
        # keep this class variable in the loop because it needs to reset each time.
        avg = analyzeData(price_craigslist, parsed_link)

        avg.getAveragePrice() # average price calculations 

        avg.compare() # compare the prices (super simple if statement)
        time.sleep(5)

    avg.writeToJsonFile() # write to the json file
    print('Done')

main()