export CUSTOM_COMPILE_COMMAND="make update-deps"
export PIP_INDEX_URL=https://$(GEMFURY_PULL_TOKEN):@pypi.fury.io/topsport-com-au/
export PIP_EXTRA_INDEX_URL=https://pypi.org/simple

_prereqs: _check-env
	python -m pip install --upgrade pip
	python -m pip install --upgrade pip-tools setuptools wheel

_update-deps:
	python -m piptools compile \
	--no-index \
	--upgrade \
	--build-isolation \
	--generate-hashes \
	--allow-unsafe \
	--output-file requirements/main.txt \
	requirements/main.in
	pip-compile \
	--no-index \
	--upgrade \
	--build-isolation \
	--generate-hashes \
	--allow-unsafe \
	--output-file requirements/dev.txt \
	requirements/dev.in

_init:
	python -m piptools sync requirements/main.txt requirements/dev.txt

_check-env:
ifndef VIRTUAL_ENV
	$(error Not in virtual environment)
endif

update: _prereqs _update-deps _init
update-deps: _prereqs _update-deps
init: _prereqs _init

mkenv:
	python -m venv .venv --copies --prompt venv

.PHONY: update-deps _update-deps init _init update _check_env mkenv