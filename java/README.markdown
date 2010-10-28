Java Fido
=========
This is a Java wrapper for Fido.

Currently, it just has stubs for PRONOM, so it can download the latest signature file.

java -jar java-fido-0.0.1-SNAPSHOT.jar

Of course, if you are behind a proxy, you'll have to tell Java about it.

java -Dhttp.proxyHost=bspcache.bl.uk -Dhttp.proxyPort=8080 \
     -Dhttp.proxyUser=username -Dhttp.proxyPassword=password \
     -jar java-fido-0.0.1-SNAPSHOT.jar

Working with the PRONOM service
-------------------------------
To save re-building the stubs all the time, the PRONOM stubs have been checked 
in under the source tree. If you wish to rebuild the stubs, you can use:

  mvn -Pbuild-stubs generate-sources

Note, however, that this will not automatically download the latest WSDL. There 
were some minor issues with the WSDL which meant they had to be cached and 
patched manually (see comments tagged as 'ANJ' in the WSDL files). To make this
possible, a catalogue file has been used to replace the remote references with 
local copies.
