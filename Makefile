PYTHON_SOURCES = msgpack test setup.py

.PHONY: all
all: cython
	python setup.py build_ext -i -f

.PHONY: format
format:
	pipx run ruff format $(PYTHON_SOURCES)

.PHONY: lint
lint:
	pipx run ruff check $(PYTHON_SOURCES)

.PHONY: doc
doc:
	cd docs && sphinx-build -n -v -W --keep-going -b html -d doctrees . html

.PHONY: pyupgrade
pyupgrade:
	@find $(PYTHON_SOURCES) -name '*.py' -type f -exec pyupgrade --py37-plus '{}' \;

.PHONY: cython
cython:
	cython msgpack/_cmsgpack.pyx

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
	docker pull quay.io/pypa/manylinux2014_i686
	docker pull quay.io/pypa/manylinux2014_x86_64
	docker pull quay.io/pypa/manylinux2014_aarch64

.PHONY: linux-wheel
linux-wheel:
	docker run --rm -v `pwd`:/project -w /project quay.io/pypa/manylinux2014_i686   bash docker/buildwheel.sh
	docker run --rm -v `pwd`:/project -w /project quay.io/pypa/manylinux2014_x86_64 bash docker/buildwheel.sh

.PHONY: linux-arm64-wheel
linux-arm64-wheel:
	docker run --rm -v `pwd`:/project -w /project quay.io/pypa/manylinux2014_aarch64   bash docker/buildwheel.sh
