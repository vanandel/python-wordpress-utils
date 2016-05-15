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

    def uploadMedia(self, presenter, title, reference, date_str, media_fname, verbose=False):
	offset = 0
	increment = 5 #20
	while True:
            if verbose:
		print "GetPosts(number=", increment, "offset = ", offset, ")"
	    pages = self.client.call(posts.GetPosts({'number': increment, 
		'offset': offset,'post_type': 'page'}))
	    offset += increment
	    #pages = self.client.call(posts.GetPosts({'post_type': 'page'}))
#		'post_type': 'page', 'id' : self.pageid}))
	    if len(pages) == 0:
		print 'No more pages'
		break
	    for p in pages:
		if verbose:
		    print "Title = ", p.title, "Id =",  p.id
		if p.id == self.pageid:
		    if verbose: print "calling self.uploadFile()"
		    # upload the audio/video file
		    media_url = self.uploadFile(date_str, media_fname, verbose)
		   
		    template = """<p align="left">{0} : {1} - {2} - {3} <a href="{4}">Play MP3</a></p>"""
		    line = template.format(date_str, presenter, title, reference, media_url)
		    # put new content at the front.
		    p.content = line + p.content
		    p.post_status = 'publish'               
		    
		    return self.client.call(posts.EditPost(p.id, p))
                
    
        
                
    def uploadMedia2(self, date_str, label,  media_fname, notes_file):
        pages = self.client.call(posts.GetPosts({'post_type': 'page', 'id' : self.pageid}))
        for p in pages:
            print "Title = ", p.title, "Id =",  p.id
            if p.id == self.pageid:
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
    h.uploadMedia("Art", "Lost and Really Lost", "Luke 15", "2015/01/05", "/Users/vanandel/tmp/test_audio/12-28-14.mp3");
    print 'uploadMedia complete'
