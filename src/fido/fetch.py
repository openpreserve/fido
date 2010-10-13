'''
Created on 13 Oct 2010

@author: AFarquha
'''

import urllib
u = urllib.urlopen("http://www.google.com", 4)
s = u.read()
print u.geturl()
print u.info()
