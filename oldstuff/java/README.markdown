Java Fido
=========
This is a Java wrapper for Fido.

Currently, it just uses the planets-suite.tecjreg stubs for PRONOM, so it can download the latest signature file.

    java -jar java-fido-0.0.1-SNAPSHOT.jar

If you are behind a proxy, you'll have to tell Java about it.

    java -Dhttp.proxyHost=bspcache.bl.uk -Dhttp.proxyPort=8080 \
         -Dhttp.proxyUser=username -Dhttp.proxyPassword=password \
         -jar java-fido-0.0.1-SNAPSHOT.jar

