import requests
from bs4 import BeautifulSoup
import os, os.path
import requests
from WPUploadMedia import WPUploadMedia


def fetchfile(url, output_fname, chunksize= 65536):
    r = requests.get(url, stream = True)
    with open(output_fname, 'wb') as fd:
        for chunk in r.iter_content(chunksize):
            fd.write(chunk) 
        #print 'finished writing ', output_fname

def scrapeit(url):    

    #site_prefix = "http://www.crestviewchurch.org/site/"
    wpu = WPUploadMedia()
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,'lxml')
    lines = soup.find_all('p')

# we're processing tuples of the form:
#  (u'2016-03-27 : Pastor Mark Quist \u2013 He is Risen Indeed! \u2013 Phil 3:7-11 ', 
#  <a href="https://crestview3665.files.wordpress.com/2015/01/2016-03-27.mp3">Play MP3</a>)
    sep = u'\u2013'
    lines.reverse()
    for l in lines:
        t = tuple(l.children)
        
        if 2== len(t) :
            print 'tuple = ', t
            ustr = t[0]
            colonIndex = ustr.find(':')
            print 'colonIndex =', colonIndex
            if colonIndex == -1:
                continue  # skip lines that don't have 'date : presenter'
            dateStr = ustr[0:colonIndex-1]
            print 'date =', dateStr 
            dash = ustr.find(sep)
            presenter = ustr[colonIndex+2:dash-1]
            print 'presenter =', presenter
            dash2 = ustr.find(sep, dash+1)
            title = ustr[dash+1:dash2]
            reference = ustr[dash2+1:-1]
           
            # well-formed entry has an MP3
            if t[1].has_attr('href'):
                link = t[1]['href']
            else:
                continue

            
            wpu.createMP3Post(presenter, title, reference, dateStr, link)




if __name__ == '__main__':
    url = "http://www.crestviewchurch.org/messages"
    scrapeit(url)

