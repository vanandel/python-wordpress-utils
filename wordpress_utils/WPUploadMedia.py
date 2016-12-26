import os,os.path
import mimetypes

from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import posts,media
from wordpress_xmlrpc.compat import xmlrpc_client


from wordpress_xmlrpc.compat import ConfigParser


class WPUploadMedia:

    def __init__(self):
        config = ConfigParser()
        print 'opening wp-config.cfg from ', os.getcwd()
        with open('wp-config.cfg', 'r') as f:
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
        titleTemplate = u"""{0} : {1} - {2}"""
        #title = title.encode('ascii','ignore')
        post.title = titleTemplate.format(date_str, presenter, title)

        template = u"""<a href="{4}">{0} : {1} - {2} - {3}</a>"""
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

    def uploadMedia(self, presenter, title, reference, date_str, media_fname, verbose=False):
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

                    template = """<p align="left">{0} : {1} - {2} - {3} <a href="{4}">Play MP3</a></p>"""
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
                        return None # until we get podcasts working again.
                        return self.createMP3Post(presenter, title, reference, date_str, media_url, verbose)





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
    result = h.uploadMedia("Pastor Mark Quist", "Biblical WorldView", "Genesis 1", "2016/12-22", 
                           "../test_audio/2016-09-11.mp3", verbose=True)
    print 'uploadMedia complete returned', result
