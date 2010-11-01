# Fido Makefile

install: setup.py fido/*.py fido/formats.py
	python setup.py install
	
dist: formats
	python setup.py sdist bdist_msi
	
formats: fido/formats.py

formats.py: fido/prepare.py fido/conf/*.zip
	python fido/prepare.py
	
clean:
	rm -rf build
	rm fido/*.pyc