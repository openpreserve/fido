# Fido Makefile
python=python
python26=/cygdrive/e/apps/python26/python
python27=/cygdrive/e/apps/python27/python

install: setup.py fido/*.py fido/*.bat fido/*.sh fido/conf/*.*
	${python26} setup.py install
	${python27} setup.py install

dist: formats
	${python26} setup.py bdist_msi
	${python27} setup.py sdist bdist_msi
	
formats: fido/conf/formats.xml fido/conf/format_extensions.xml

fido/conf/formats.xml: fido/prepare.py fido/conf/*.zip
	${python} fido/prepare.py
	
all: clean install test dist

test: test/ok1.txt test/ok2.txt test/ok3.txt
	
# Need to remember how to error properly
test/ok1.txt test/ok2.txt test/ok3.txt: test/expected.csv testrun
	(diff  test/expected.csv test/out-1.csv) && (echo 'success' > test/ok1.txt)
	(diff  test/expected.csv test/out-2.csv) && (echo 'success' > test/ok2.txt)
	(diff  test/expected.csv test/out-3.csv) && (echo 'success' > test/ok3.txt)

ok="{info.filename},{info.puid},{info.signaturename}\n"
ko="{info.filename},NONE,NONE\n"

testrun:  test/files.txt
	# Regular run
	${python} -u -m fido.run -r -z \
		-matchprintf ${ok} -nomatchprintf ${ko} test/files | sort > test/out-1.csv
	# with input from pipe
	find test/files -type f | ${python} -u -m fido.run -r -z -i - \
		-matchprintf ${ok} -nomatchprintf ${ko} | sort > test/out-2.csv
	# with input from file
	${python} -u -m fido.run -r -z -i test/files.txt \
		-matchprintf ${ok} -nomatchprintf ${ko} | sort > test/out-3.csv

	# with input from stream
	# with input from multi-stream
	
test/files.txt: test/files/*.*
	find test/files -type f > test/files.txt

clean:
	rm -rf build
	rm -f fido/*.pyc
	rm -f test/out*.csv test/test.txt