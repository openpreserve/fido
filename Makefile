# Fido Makefile

python=python
python26=python2.6 #/cygdrive/e/apps/python26/python
python27=python #/cygdrive/e/apps/python27/python
xmllint=/usr/bin/xmllint

ok="{info.filename},{info.puid},{info.signaturename}\n"
ko="{info.filename},NONE,NONE\n"

app_files=setup.py fido/argparselocal.py fido/fido.bat fido/fido.sh fido/__init__.py fido/testfido.py
xml_files=fido/conf/formats.xml fido/conf/format_extensions.xml
doc_files=README.txt LICENSE.txt

.PHONY:all clean dist prof test install

all: test install dist

README.txt: README.in fido/fido.py
	${python} fido/fido.py -h > README.txt
	cat README.in >> README.txt

clean:
	rm -rf build
	rm -f fido/*.pyc
	rm -f test/out*.*
	rm -f test/prof/*.prof
	rm -f make/*

install: make/install

make/install: ${app_files} ${xml_files} ${doc_files}
	${python26} setup.py install
	${python27} setup.py install
	touch make/install

dist: make/dist

make/dist: ${app_files} ${xml_files} ${doc_files}
	${python26} setup.py bdist_msi
	${python27} setup.py sdist bdist_msi
	touch make/dist

convert: fido/conf/pronom-xml.zip fido/fido.py fido/conf/fido-formats.xsd
	${python} fido/fido.py -convert -source fido/conf/pronom-xml.zip -target fido/conf/formats.xml
	#${xmllint} -noout -schema fido/conf/fido-formats.xsd -valid fido/conf/formats.xml
	${xmllint} -format fido/conf/formats.xml -o fido/conf/formats.xml

prof: make/prof

make/prof: ${app_files) ${xml_files}
	python -m cProfile -o test/prof/convert.prof fido/fido.py -i fido/conf/pronom-xml.zip -o test/out-formats.xml
	python -m cProfile -o test/prof/id-test-r.prof fido/fido.py -r -conf fido/conf test/files
	python -m cProfile -o test/prof/id-to-read-r.prof fido/fido.py -r -conf fido/conf 'c:\Documents and Settings\afarquha\My Documents\00_To_Read'
	touch make/prof
	
test: make/test.run make/test.prep make/test.args

make/test.prep: install
	${python} -u -m fido.fido -input fido/conf/pronom-xml.zip -output test/out-prep.xml
	(diff test/expected-prep.xml test/out-prep.xml)
	touch make/test.prep

make/test.run: install
	find test/files -type f > test/files.txt
	# Regular run
	${python} -u -m fido.fido -r -z \
		-matchprintf ${ok} -nomatchprintf ${ko} test/files | sort > test/out-1.csv
	# with input from pipe
	find test/files -type f | ${python} -u -m fido.fido -r -z -in - \
		-matchprintf ${ok} -nomatchprintf ${ko} | sort > test/out-2.csv
	# with input from file
	${python} -u -m fido.fido -r -z -in test/files.txt \
		-matchprintf ${ok} -nomatchprintf ${ko} | sort > test/out-3.csv
	# with configuration directory specified on command line
	${python} -u -m fido.fido -conf test/conf -r -z \
		-matchprintf ${ok} -nomatchprintf '' test/files | sort > test/out-4.csv
	(diff  test/expected.csv test/out-1.csv)
	(diff  test/expected.csv test/out-2.csv)
	(diff  test/expected.csv test/out-3.csv)
	(diff  test/expected-4.csv test/out-4.csv)
	touch make/test.run

make/test.args: install
	${python} -u -m fido.fido -show defaults > test/out-args-1.txt
	(diff test/expected-args-1.txt test/out-args-1.txt)
	${python} -u -m fido.fido -show formats > test/out-args-2.txt
	(diff test/expected-args-2.txt test/out-args-2.txt)
	
