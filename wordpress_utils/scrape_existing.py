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

    site_prefix = "http://www.crestviewchurch.org/site/"
    wpu = WPUploadMedia()
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,'lxml')
    lines = soup.find_all('p')
    
    # fetch new content, find last entry
    content = wpu.getContent()
    earliestLine = BeautifulSoup(content,'lxml').findAll('p')[-1]
    earliestDate = earliestLine.text.split()[0]
    
    
    for l in lines:
        t = tuple(l.children)
        if 2 <= len(t) and len(t) <=4:
            # extract description, e.g. 10/14 Pastor Art DeBruyn - Romans 9 - The Simple Narrative -
            desc = " ".join(map(str, t[0].split()[1:]))
            # extract link, MessagesFlash/audio_player_files/music/01-04-15.mp3, 
            # or ..//site/MessagesFlash/audio_player_files/music/01-08-12.mp3
            if t[1].has_attr('href'):
                link = site_prefix+t[1]['href']
            else:
                continue
            
            # transform MM-DD-YY to ISO date: 2015-01-04
            mmddyy = os.path.basename(link)[0:-4].split('-')
            iso_date_str = "20{0}-{1}-{2}".format(mmddyy[2], mmddyy[0], mmddyy[1])
            if iso_date_str >= earliestDate:
                print 'Skipping ', iso_date_str
                continue
                
            desc = iso_date_str + " " + desc
        
            
            mp3 = os.path.join('/tmp', iso_date_str+'.mp3')
            fetchfile(link, mp3)
        
            
            pdf = None
            if len(t) == 4:
                dload_pdf = site_prefix+t[3]['href']
                pdf = os.path.join('/tmp', os.path.basename(dload_pdf))
                fetchfile(dload_pdf, pdf)
            print 'mp3 = ', mp3, ' pdf=', pdf, ' desc =', desc
            wpu.uploadMedia2(iso_date_str, desc, mp3, pdf)
    
       
       

if __name__ == '__main__':
    url = "http://www.crestviewchurch.org/site/Archives.html"
    scrapeit(url)
    