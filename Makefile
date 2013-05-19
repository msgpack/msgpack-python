.PHONY: test all python3

all: cython
	python setup.py build_ext -i -f

doc-serve: all
	cd docs && make serve

doc:
	cd docs && make zip

cython:
	cython --cplus msgpack/*.pyx

python3: cython
	python3 setup.py build_ext -i -f

test:
	py.test test
