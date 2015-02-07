import requests
from bs4 import BeautifulSoup


def scrapeit(url):    

    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,'lxml')
    lines = soup.find_all('p')
    l = lines[-3]
    print l

if __name__ == '__main__':
    url = "http://www.crestviewchurch.org/site/Archives.html"
    scrapeit(url)
    