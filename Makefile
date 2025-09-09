#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

.PHONY: init
init:
	python3 -m pip install --upgrade build

.PHONY: build
build:
	python3 -m build

.PHONY: test
test:
	py.test
