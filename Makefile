# Fido Makefile

python='e:\Apps\Python26\python.exe'

install: setup.py fido/*.py fido/fido.bat fido/fido.sh
	${python} setup.py install
	
dist: formats
	${python} setup.py sdist bdist_msi
	
formats: fido/formats.py

formats.py: fido/prepare.py fido/format_fixup.py fido/conf/*.zip
	${python} fido/prepare.py
	
clean:
	rm -rf build
	rm fido/*.pyc