.PHONY: clean package package-deps package-source package-upload package-wheel

package-deps:
	pip install --upgrade twine wheel

package-source:
	python setup.py sdist

package-wheel: package-deps
	python setup.py bdist_wheel --universal

package-upload: package-deps package-source package-wheel
	twine upload dist/* --repository-url https://upload.pypi.org/legacy/

package: package-upload

clean:
	rm -rf opf_fido.egg-info/
	rm -rf build/
	rm -rf dist/
