#!/usr/bin/env python

import re, urllib, urlparse

url_pattern = "http://digitalcorpora.org/corp/nps/files/govdocs1/%03i/"

def main():
    extensions = {}
    for url in urls():
        print url
        extension = url.split(".")[-1]
        extensions[extension] = extensions.get(extension, 0) + 1
    print extensions

def urls():
    for i in range(0, 1000):
        url = url_pattern % i
        for filename in filenames(url):
            yield urlparse.urljoin(url, filename)

def filenames(url):
    html = urllib.urlopen(url).read()
    for match in re.finditer(r'<td><a href="(.+?)"', html):
        yield match.group(1)

if __name__ == "__main__":
    main()
