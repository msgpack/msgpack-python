.PHONY: all
all: cython
	python setup.py build_ext -i -f

.PHONY: cython
cython:
	cython --cplus msgpack/*.pyx

.PHONY: test
test:
	py.test -v test

.PHONY: serve-doc
serve-doc: all
	cd docs && make serve

.PHONY: clean
clean:
	rm -rf build
	rm msgpack/*.so
	rm -rf msgpack/__pycache__
	rm -rf test/__pycache__

.PHONY: linux-wheel
linux-wheel:
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux1_i686   bash docker/buildwheel.sh
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux1_x86_64 bash docker/buildwheel.sh
