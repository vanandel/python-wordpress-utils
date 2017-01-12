import os,os.path,sys
import mimetypes

from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import posts,media
from wordpress_xmlrpc.compat import xmlrpc_client
import requests


from wordpress_xmlrpc.compat import ConfigParser

def fetchfile(url, output_fname, chunksize= 65536):
    r = requests.get(url, stream = True)
    with open(output_fname, 'wb') as fd:
        for chunk in r.iter_content(chunksize):
            fd.write(chunk) 
        #print 'finished writing ', output_fname

class WPUploadMedia:

    def __init__(self, configFile='wp-config.cfg'):
        config = ConfigParser()
        print 'opening {0} from {1}'.format(configFile,os.getcwd())
        with open(configFile, 'r') as f:
            config.readfp(f)

        self.xmlrpc_url = config.get('wordpress', 'url')
        self.username = config.get('wordpress', 'username')
        self.userid = config.get('wordpress', 'userid')
        self.post_title = config.get('wordpress', 'post_title')
        self.feed_category = config.get('wordpress', 'feed_category')
        self.client = Client(self.xmlrpc_url,
                             self.username,
                             config.get('wordpress', 'password'))

    def uploadFile(self, date_str, file, verbose=False):
        if verbose: print "starting encoding ", file
        suffix = os.path.splitext(file)[1]
        data = {'name': date_str+suffix}
        data['type'] = mimetypes.guess_type(file)[0]         
        # read the binary file and let the XMLRPC library encode it into base64        
        with open(file, 'rb') as f:
            data['bits'] = xmlrpc_client.Binary(f.read())  

        if verbose: print "encoding complete - starting upload"

        response = self.client.call(media.UploadFile(data))
        if verbose: print "upload complete"
        return response['url']

    """create a post for this MP3 - WordPress will update the RSS feed """
    def createMP3Post(self, presenter, title, reference, date_str, media_url, verbose=False):
        if verbose:
            print 'createMP3Post starting'


        post = WordPressPost()
        titleTemplate = u"""Podcast : {0} : {1} - {2}"""
        #title = title.encode('ascii','ignore')
        post.title = titleTemplate.format(date_str, presenter, title)

        template = u"""[audio  "{4}" ]<p>{0} : {1} - {2} - {3}</p>"""
        post.content = template.format(date_str, presenter, title, reference, media_url)
        post.post_status = 'publish'
        # set the category so this Post is inserted into our 'podcast' feed
        post.terms_names = {'category': [self.feed_category,]}
        post.post_format = 'Link'

        #term = WordPressTerm()
        #post.terms = [term,]
        retval = None
        try:
            retVal = self.client.call(posts.NewPost(post))
        except Exception as inst:
            print 'createMP3Post: posts.NewPost() failed', inst
        else:
            if verbose:
                print 'createMP3Post complete'
            return retVal

    def uploadMedia(self, presenter, title, reference, date_str, media_fname, createPost=True,verbose=False):
        offset = 0
        increment = 5 #20
        print 'self.post_title = ', self.post_title, ' type(self.post_title)  = ', type(self.post_title)
        while True:
            if verbose:
                print "GetPosts(number=", increment, "offset = ", offset, ")"
            pages = self.client.call(posts.GetPosts({'number': increment, 
                                                     'offset': offset,'post_type': 'page'}))
            offset += increment
            if len(pages) == 0:
                print 'No more pages'
                break
            for p in pages:
                if verbose:
                    print "Title = '", p.title, "' Id =",  p.id, 'type(p.title)', type(p.title)
                if p.title == self.post_title:
                    if verbose: print "calling self.uploadFile()"
                    # upload the audio/video file
                    media_url = self.uploadFile(date_str, media_fname, verbose)

                    template = """<p align="left">{0} : {1} - {2} - {3} <a href="{4}">Play MP3</a></p>\n"""
                    # strip out characters we don't understand - better than crashing!
                    title = title.encode('ascii','ignore')
                    line = template.format(date_str, presenter, title, reference, media_url)
                    # put new content at the front.
                    p.content = line + p.content
                    p.post_status = 'publish'               
                    # magic : avoid 'Invalid attachment ID.' exception from EditPost
                    p.thumbnail = None  
                    if verbose: 
                        print 'upload complete, url = ', media_url, 'adding line=', line
                        print 'post = ', p


                    try:
                        self.client.call(posts.EditPost(p.id, p))
                        if verbose: print 'post.EditPost complete'
                    except Exception as inst:
                        print 'uploadMedia: posts.EditPost() failed', inst
                        return None
                    else:
                        if createPost: return self.createMP3Post(presenter, title, reference, date_str, media_url, verbose)
                        return None




    def uploadMedia2(self, date_str, label,  media_fname, notes_file):
        pages = self.client.call(posts.GetPosts({'post_type': 'page', 'title' : self.post_title}))
        for p in pages:
            print "Title = ", p.title, "Id =",  p.id
            if p.title == self.post_title:
                # upload the audio/video file first

                mp3_url = self.uploadFile(date_str, media_fname, verbose=True)


                #print p.content
                if notes_file:
                    # if we have a notes file, upload it.
                    pdf_url = self.uploadFile(date_str, notes_file)
                    line = """<p align="left">{0}  <a href="{1}">Play MP3</a><a href="{2}">; Discussion Questions</a></p>""".format(label, mp3_url, pdf_url)
                else:
                    line = """<p align="left">{0}  <a href="{1}">Play MP3</a></p>""".format(label, mp3_url)

                # put new content at the end.
                p.content = p.content + line
                p.post_status = 'publish'               

                return self.client.call(posts.EditPost(p.id, p))  

    def getContent(self):
        pages = self.client.call(posts.GetPosts({'post_type': 'page', 'id' : self.pageid}))
        for p in pages:
            # print p.title
            #print p.id
            if p.id == self.pageid:
                return p.content

        return None

if __name__ == '__main__':
    h = WPUploadMedia()
    presenter='Pastor Mark Quist'
    title = "still more testing"
    reference = "Genesis 4"
    date_str =  "2017-01-01"
    media_url =  "https://crestviewchurch.files.wordpress.com/2016/12/2016-12-241.mp3"
    if len(sys.argv) > 1 and sys.argv[1] == 'podcast' :
        result = h.createMP3Post(presenter, title, reference, date_str, 
                                media_url, verbose=True)
        
        title = "testing #2"
        reference = "Genesis 2"
        date_str =  "2016-12-31"        
        print 'createMP3Post() returned', result
        result = h.createMP3Post(presenter, title, reference, date_str, 
                                 media_url, verbose=True)   
        print 'createMP3Post() returned', result
    else:
    
        result = h.uploadMedia(presenter,title ,reference,date_str, 
                           "../test_audio/2016-09-11.mp3", verbose=True)
        print 'uploadMedia() complete returned', result
