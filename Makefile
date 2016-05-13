.PHONY: test all python3

all: cython
	python setup.py build_ext -i -f

doc-serve: all
	cd docs && make serve

doc:
	cd docs && make zip

upload-doc:
	python setup.py upload_docs --upload-dir docs/_build/html

cython:
	cython --cplus msgpack/*.pyx

python3: cython
	python3 setup.py build_ext -i -f

test:
	py.test test

.PHONY: clean
clean:
	rm -rf build
	rm msgpack/*.so
	rm -rf msgpack/__pycache__
