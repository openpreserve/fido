#!/bin/bash
base="http://www.nationalarchives.gov.uk/pronom/"
re='PUID=\"(fmt|x-fmt)/([0-9]+)\"'

while read line; do
	 if [[ $line =~ $re ]] ;	then
	   puid=${BASH_REMATCH[1]}/${BASH_REMATCH[2]}
	   fname=xml/puid.${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.xml
	   wget -T5 -O $fname $base$puid.xml
	 fi
done
