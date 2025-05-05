"""

TODO: 
    STEP 1: Parse data from the craigslist products file and make sure to get 
           simplified product names and prices
    
    STEP 2: Use the simplified product names to search for the same products on eBay
           and get the prices for those products

    STEP 3: Compare the prices from craigslist and eBay and find the best deal
           for each product. If the eBay price is lower, print the product name and

"""

import requests
from bs4 import BeautifulSoup
import numpy
import json
import time
import os
import datetime

class parseData:
    # in this section we need to open the craigslist products file and get the price, simplified name and the link to the product 
    # the reason why we need the link btw is for the front end later on
    # btw everything will be written in the finalProduct.json file
    # the finalProduct.json file will be used to display the data on the front end which will be refreshing every now and then. Probably an hour or so to get un IP banned from craigslist


    def __init__(self,):
        self.products = []
        self.filePath = "json/craigslistProducts.json"
        self.finalFilePath = "json/finalProduct.json"
        self.index = 0

        # we need to append, price, product, possibly image link?
        self.finalProducts = []

        # open the file in a self class
        self.data = self.openFiles()

    def openFiles(self):
        with open(self.filePath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    
    def getData(self):
        if self.index < len(self.data):
            main_data = self.data[self.index]

            # get lnik, title descriptoin, price, simplified title
            link = main_data['link']
            title = main_data['title']
            description = main_data['description']
            price = main_data['price']
            simplified_title = main_data['simplified_title']

            return link, title, description, price, simplified_title
        else:
            return None
        
    def goNext(self):
        self.index += 1

def main():
    # this is the main function that will run the program
    # we need to get the data from the craigslist products file and then search for the same products on eBay
    # we will use the parseData class to get the data from the craigslist products file
    # then we will use the ebayScan class to search for the same products on eBay

    # first we need to get the data from the craigslist products file
    craigslist = parseData()

    while True:
        q = craigslist.getData() # get the parsed data to pass through the ebayScan class and the price comparisons

        if q is None:
            break
        else:
            print(q)
            craigslist.goNext()

        #break # for testing break the loop so ti doesn't do it like a million times


main()