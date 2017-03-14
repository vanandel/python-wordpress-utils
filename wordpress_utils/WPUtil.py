import os,os.path,sys
import mimetypes

from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import posts,media
from wordpress_xmlrpc.compat import xmlrpc_client


from wordpress_xmlrpc.compat import ConfigParser



class WPUtil():

    def __init__(self, configFile='wp-config.cfg'):
        config = ConfigParser()
        with open(configFile, 'r') as f:
            config.readfp(f)

        self.client = Client( config.get('wordpress', 'url'),
            config.get('wordpress', 'username'),
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


    def findPageByTitle(self,  theTitle, verbose=False):
        offset = 0  # starting page
        increment = 20 # how many pages to fetch at once
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
                if p.title == theTitle:
                    return p
       
        raise LookupError('can not find page titled {0}'.format(theTitle))
    
    def prependToPage(self, page, theString):
        # put new content at the front.
        page.content = theString + page.content
        page.post_status = 'publish'               
        
        page.thumbnail = None  # magic : avoid 'Invalid attachment ID.' exception from EditPost
        try:
            self.client.call(posts.EditPost(page.id, page))
        except Exception as inst:
            print 'uploadMedia: posts.EditPost() failed', inst        
        

    def getContent(self, theTitle):
        try:
            p = self.findPageByTitle(theTitle)
        except LookupError as err:
            print err.args
        return p.content
    
    """create a post with the specified title, content, category """
    def createPost(self, title, content, category, post_format = 'Standard'):
        
        post = WordPressPost()
        post.title = title.encode('ascii','ignore')

        post.content = content.encode('ascii','ignore')
        post.post_status = 'publish'
        # set the category so this Post is inserted into the correct feed
        post.terms_names = {'category': [category,]}
        post.post_format = post_format

        return self.client.call(posts.NewPost(post))

if __name__ == '__main__':
    wpu = WPUtil()
    p = wpu.findPageByTitle('demo')
    content = p.content
    print content.splitlines()[0] 
    wpu.prependToPage(p, 'a new first line\n')
    newPage = wpu.findPageByTitle('demo')
    print newPage.content.splitlines()[0]
