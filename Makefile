# Fido Makefile
python=python

install: setup.py fido/*.py fido/fido.bat fido/fido.sh
	${python} setup.py install
	
dist: formats
	${python} setup.py sdist bdist_msi
	
formats: fido/formats.py

formats.py: fido/prepare.py fido/format_fixup.py fido/conf/*.zip
	${python} fido/prepare.py

# Need to remember how to error properly
test: test/expected.csv test/test.txt
	diff  test/expected.csv test/out-1.csv
	diff  test/expected.csv test/out-2.csv
	diff  test/expected.csv test/out-3.csv

ok="{info.name},{format.Identifier},{sig.SignatureName}\n"
ko="{info.name},NONE,NONE\n"

test/test.txt:  test/files.txt
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
	touch test/test.txt
	
test/multi.txt: 
	
test/files.txt: test/files/*.*
	find test/files -type f > test/files.txt

clean:
	rm -rf build
	rm fido/*.pyc