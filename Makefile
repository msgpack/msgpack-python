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

build-manylinux1-wheel:
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux1_i686   bash docker/buildwheel.sh
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux1_x86_64 bash docker/buildwheel.sh
