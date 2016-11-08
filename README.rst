Overview
========

Python utilities using the WordPress blog's `XML-RPC API`__.

__ http://codex.wordpress.org/XML-RPC_Support

This library was developed against and tested on WordPress 3.5.
This library is compatible with Python 2.6+ and 3.2+.
This library depends on the python-wordpress-xmlrpc library

You will need to create a wp-config.cfg file of the form::

  [wordpress]
  url = https://crestview3665.wordpress.com/xmlrpc.php
  username = your_user_name
  password = your_password
  userid = 1
  pageid = 200

Please see docs for more information: http://python-wordpress-utils.rtfd.org
