#!/usr/bin/env python
from wordpress_utils.WPUploadMedia import WPUploadMedia
if __name__ == '__main__':
    h = WPUploadMedia()
    result = h.uploadMedia("Pastor Mark Quist", "Biblical WorldView", "Genesis 1", "2016/12-22", "test_audio/2016-09-11.mp3")
    print 'uploadMedia complete returned', result
