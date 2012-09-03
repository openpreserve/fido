#!/usr/bin/env python

"""
Downloads files from govdocs1 project for use in testing. 

    http://digitalcorpora.org/corpora/files

It should download an example file for every file extension. It will
write out a manifest.txt of all the filenames and their urls.
"""

import os, re, urllib, urlparse

url_pattern = "http://digitalcorpora.org/corp/nps/files/govdocs1/%03i/"

def main():
    govdocs1 = open("govdocs1.txt", "w")
    manifest = open("manifest.txt", "w")
    counts = {}
    for url in urls():
        govdocs1.write("%s\n" % url)
        ext = url.split(".")[-1]
        counts[ext] = counts.get(ext, 0) + 1
        filename = "fido.%s" % ext
        if not os.path.isfile(filename):
            manifest.write("%s %s\n" % (filename, url))
            urllib.urlretrieve(url, filename)
    print counts
    manifest.close()
    govdocs1.close()

def urls():
    for i in range(0, 1000):
        url = url_pattern % i
        for filename in filenames(url):
            if filename.startswith("/"):
                continue
            yield urlparse.urljoin(url, filename)

def filenames(url):
    html = urllib.urlopen(url).read()
    for match in re.finditer(r'<td><a href="(.+?)"', html):
        yield match.group(1)

if __name__ == "__main__":
    main()
