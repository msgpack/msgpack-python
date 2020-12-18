.PHONY: all
all: cython
	python setup.py build_ext -i -f

.PHONY: black
black:
	black msgpack/ test/ setup.py

.PHONY: cython
cython:
	cython --cplus msgpack/_cmsgpack.pyx

.PHONY: test
test: cython
	pip install -e .
	pytest -v test
	MSGPACK_PUREPYTHON=1 pytest -v test

.PHONY: serve-doc
serve-doc: all
	cd docs && make serve

.PHONY: clean
clean:
	rm -rf build
	rm -f msgpack/_cmsgpack.cpp
	rm -f msgpack/_cmsgpack.*.so
	rm -f msgpack/_cmsgpack.*.pyd
	rm -rf msgpack/__pycache__
	rm -rf test/__pycache__

.PHONY: update-docker
update-docker:
	docker pull quay.io/pypa/manylinux1_i686
	docker pull quay.io/pypa/manylinux1_x86_64

.PHONY: linux-wheel
linux-wheel:
	docker run --rm -v `pwd`:/project -w /project quay.io/pypa/manylinux1_i686   bash docker/buildwheel.sh
	docker run --rm -v `pwd`:/project -w /project quay.io/pypa/manylinux1_x86_64 bash docker/buildwheel.sh

.PHONY: linux-arm64-wheel
linux-arm64-wheel:
	docker run --rm -v `pwd`:/project -w /project quay.io/pypa/manylinux2014_aarch64   bash docker/buildwheel.sh
