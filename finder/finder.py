import requests
from bs4 import BeautifulSoup
import json

def main():
    r = requests.get('https://www.craigslist.org/about/sites')

    soup = BeautifulSoup(r.content, 'html.parser')

    s = soup.find('div', class_="colmask")

    content = soup.find_all('a', href=True)

    final = []

    for a in content:
        final.append(a['href'])

    #content = soup.prettify(content)     print(content)

    json_object = json.dumps(final, indent=4)

    
    with open("cities.json", "w")as f:
        f.write(json_object)
    


main()