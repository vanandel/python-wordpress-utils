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
        with open('wp-config.cfg', 'r') as f:
            config.readfp(f)

        self.xmlrpc_url = config.get('wordpress', 'url')
        self.username = config.get('wordpress', 'username')
        self.userid = config.get('wordpress', 'userid')
        self.pageid = config.get('wordpress', 'pageid')
        self.client = Client(self.xmlrpc_url,
                             self.username,
                             config.get('wordpress', 'password'))


    def uploadMedia(self, presenter, title, reference, date_str, media_fname):
        pages = self.client.call(posts.GetPosts({'post_type': 'page', 'id' : self.pageid}))
        for p in pages:
           # print p.title
            #print p.id
            if p.id == self.pageid:
                # upload the audio/video file first
                suffix = os.path.splitext(media_fname)[1]
                data = {'name': date_str+suffix}
                data['type'] = mimetypes.guess_type(media_fname)[0] 
                # read the binary file and let the XMLRPC library encode it into base64
                print "starting encoding"
                with open(media_fname, 'rb') as f:
                    data['bits'] = xmlrpc_client.Binary(f.read())  
                
                print "encoding complete - starting upload"
                    
                response = self.client.call(media.UploadFile(data))
                print "upload complete"
                
                print p.content
               
                template = """<p align="left">{0} : {1} - {2} - {3} <a href="{4}">Play MP3</a></p>"""
                line = template.format(date_str, presenter, title, reference, response['url'])
                # put new content at the front.
                p.content = line + p.content
                p.post_status = 'publish'               
                
                self.client.call(posts.EditPost(p.id, p))                


if __name__ == '__main__':
    h = WPUploadMedia()
    h.uploadMedia("Art", "Lost and Really Lost", "Luke 15", "2015/01/05", "/Users/vanandel/tmp/test_audio/12-28-14.mp3");
    print 'uploadMedia complete'
