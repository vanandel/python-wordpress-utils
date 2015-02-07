#!/usr/bin/env python
from wordpress_utils.WPUploadMedia import WPUploadMedia
if __name__ == '__main__':
    h = WPUploadMedia()
    h.uploadMedia("Art", "Lost and Really Lost", "Luke 15", "2015/01/05", "/Users/vanandel/tmp/test_audio/12-28-14.mp3");
    print 'uploadMedia complete'
