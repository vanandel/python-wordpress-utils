from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import posts

import collections




from wordpress_xmlrpc.compat import ConfigParser


class ListPages():

    def __init__(self):
        config = ConfigParser()
        with open('wp-config.cfg', 'r') as f:
            config.readfp(f)

        self.xmlrpc_url = config.get('wordpress', 'url')
        self.username = config.get('wordpress', 'username')
        self.userid = config.get('wordpress', 'userid')
        self.client = Client(self.xmlrpc_url,
                             self.username,
                             config.get('wordpress', 'password'))
        
    def assert_list_of_classes(self, lst, kls):
        """
        Verifies that a list contains objects of a specific class.
        """
        assert isinstance(lst, collections.Iterable)
        
        for obj in lst:
            assert isinstance(obj, kls)    
        
#    @attr('posts')
    def list(self):
        pages = self.client.call(posts.GetPosts({'post_type': 'page'}, results_class=WordPressPage))
        assert len(pages) > 0
        self.assert_list_of_classes(pages, WordPressPage)
        for p in pages:
            print p.title, p.id
            

if __name__ == '__main__':
	l = ListPages();
	l.list();
	
    
