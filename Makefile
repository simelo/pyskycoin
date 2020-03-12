.DEFAULT_GOAL := help
.PHONY: configure build-libc build-swig develop build-libc-swig build
.PHONY: test test-ci help

# Compilation output
.ONESHELL:
SHELL := /bin/bash

PYTHON_BIN   ?= python$(PYTHON)
MKFILE_PATH   = $(abspath $(lastword $(MAKEFILE_LIST)))
REPO_ROOT     = $(dir $(MKFILE_PATH))
GOPATH_DIR    = $(REPO_ROOT)/gopath
SKYLIBC_DIR  ?= $(GOPATH_DIR)/src/github.com/fibercrypto/libskyfiber
SKYCOIN_DIR  ?= $(SKYLIBC_DIR)/vendor/github.com/SkycoinProject/skycoin
SKYBUILD_DIR  = $(SKYLIBC_DIR)/build
BUILDLIBC_DIR = $(SKYBUILD_DIR)/libskycoin
LIBC_DIR      = $(SKYLIBC_DIR)/lib/cgo
LIBSWIG_DIR   = $(REPO_ROOT)/lib/swig/swig
LIBSWIG_PYSKYFIBER = $(REPO_ROOT)/lib/swig
BUILD_DIR     = build
DIST_DIR      = dist
BIN_DIR       = $(SKYLIBC_DIR)/bin
INCLUDE_DIR   = $(SKYLIBC_DIR)/include
FULL_PATH_LIB = $(REPO_ROOT)/$(BUILDLIBC_DIR)

LIB_FILES = $(shell find $(SKYLIBC_DIR)/lib/cgo -type f -name "*.go")
SRC_FILES = $(shell find $(SKYCOIN_DIR)/src -type f -name "*.go")
SWIG_FILES = $(shell find $(LIBSWIG_DIR) -type f -name "*.i")
HEADER_FILES = $(shell find $(INCLUDE_DIR) -type f -name "*.h")

PYTHON_CLIENT_DIR = $(REPO_ROOT)/lib/skyapi

ifeq ($(shell uname -s),Linux)
	TEMP_DIR = tmp
	PYTHON_BIN = python$(PYTHON)
else ifeq ($(shell uname -s),Darwin)
	TEMP_DIR = $TMPDIR
	PYTHON_BIN = python
endif

configure: ## Configure build environment
	echo "Configure build environment"
	(cd $(LIBSWIG_PYSKYFIBER) && mkdir -p $(BUILD_DIR)/usr/tmp $(BUILD_DIR)/usr/lib $(BUILD_DIR)/usr/include)
	(cd $(LIBSWIG_PYSKYFIBER) && mkdir -p $(BUILDLIBC_DIR) $(BIN_DIR) $(INCLUDE_DIR))
	(cd $(LIBSWIG_PYSKYFIBER) && mkdir -p $(DIST_DIR))


build-libc: configure ## Build libskycoin C client library
	echo "Build libskycoin C client library"
	GOPATH="$(REPO_ROOT)/$(GOPATH_DIR)" make -C $(SKYLIBC_DIR) clean-libc
	GOPATH="$(REPO_ROOT)/$(GOPATH_DIR)" make -C $(SKYLIBC_DIR) build-libc
	mkdir -p $(LIBSWIG_PYSKYFIBER)/include
	rm -f $(LIBSWIG_PYSKYFIBER)/include/libskycoin.h
	grep -v _Complex $(SKYLIBC_DIR)/include/libskycoin.h > $(LIBSWIG_PYSKYFIBER)/include/libskycoin.h
	rm -f $(SKYLIBC_DIR)/include/libskycoin.h

build-swig: ## Generate Python C module from SWIG interfaces
	echo "Generate Python C module from SWIG interfaces"
	#Generate structs.i from skytypes.gen.h
	rm -f $(LIBSWIG_DIR)/structs.i
	cp $(INCLUDE_DIR)/skytypes.gen.h $(LIBSWIG_DIR)/structs.i
	{ \
		if [[ "$$(uname -s)" == "Darwin" ]]; then \
			sed -i '.kbk' 's/#/%/g' $(LIBSWIG_DIR)/structs.i ;\
		else \
			sed -i 's/#/%/g' $(LIBSWIG_DIR)/structs.i ;\
		fi \
	}
	rm -fv $(LIBSWIG_PYSKYFIBER)/skycoin/skycoin.py
	rm -f $(LIBSWIG_PYSKYFIBER)/pyskycoin_wrap.c
	swig -python -py3 -w501,505,401,302,509,451 -I$(LIBSWIG_PYSKYFIBER)/include/ -I$(INCLUDE_DIR) -outdir $(LIBSWIG_PYSKYFIBER)/skycoin/ -o $(LIBSWIG_PYSKYFIBER)/pyskycoin_wrap.c $(LIBSWIG_DIR)/pyskycoin.i

develop: ## Install PySkycoin for development
	(cd $(LIBSWIG_PYSKYFIBER) && $(PYTHON_BIN) setup.py develop)
	(cd $(PYTHON_CLIENT_DIR) && $(PYTHON_BIN) setup.py develop)

build-libc-swig: build-libc build-swig

build: build-libc-swig ## Build PySkycoin Python package
	(cd $(LIBSWIG_PYSKYFIBER) && GOPATH="$(REPO_ROOT)/$(GOPATH_DIR)" REPO_ROOT=$(REPO_ROOT) $(PYTHON_BIN) setup.py build)
	(cd $(PYTHON_CLIENT_DIR) && $(PYTHON_BIN) setup.py build)

test-ci: build-libc build-swig develop ## Run tests on (Travis) CI build
	(cd $(LIBSWIG_PYSKYFIBER) && tox)
	(cd $(PYTHON_CLIENT_DIR) && tox)


test-skyapi: build-libc build-swig develop ## Run project test suite by skyapi
	(cd $(PYTHON_CLIENT_DIR) && $(PYTHON_BIN) setup.py test)

test-libsky: build-libc build-swig develop ## Run project test suite by pyskycoin
	echo "Run project test suite by pyskycoin"
	(cd $(LIBSWIG_PYSKYFIBER) && REPO_ROOT=$(REPO_ROOT) $(PYTHON_BIN) setup.py test)

test: test-skyapi test-libsky ## Run project test suite

sdist: ## Create source distribution archive
	(cd $(LIBSWIG_PYSKYFIBER) && $(PYTHON_BIN) setup.py sdist --formats=gztar)
	(cd $(PYTHON_CLIENT_DIR) && $(PYTHON_BIN) setup.py sdist --formats=gztar)

bdist_wheel: ## Create architecture-specific binary wheel distribution archive
	(cd $(LIBSWIG_PYSKYFIBER) && $(PYTHON_BIN) setup.py bdist_wheel)
	(cd $(PYTHON_CLIENT_DIR) && $(PYTHON_BIN) setup.py bdist_wheel)

# FIXME: After libskycoin 32-bits binaries add bdist_manylinux_i686
bdist_manylinux: bdist_manylinux_amd64 ## Create multilinux binary wheel distribution archives

bdist_manylinux_amd64: ## Create 64 bits multilinux binary wheel distribution archives
	docker pull quay.io/pypa/manylinux1_x86_64
	docker run --rm -t -v $(REPO_ROOT):/io quay.io/pypa/manylinux1_x86_64 /io/.travis/build_wheels.sh
	ls wheelhouse/
	mkdir -p $(DIST_DIR)
	cp -v wheelhouse/* $(DIST_DIR)
	docker run --rm -t -v $(REPO_ROOT):/io quay.io/pypa/manylinux1_x86_64 /io/.travis/build_wheels_skyapi.sh
	mkdir -p $(PYTHON_CLIENT_DIR)/$(DIST_DIR)
	cp -v $(PYTHON_CLIENT_DIR)/wheelhouse/* $(PYTHON_CLIENT_DIR)/$(DIST_DIR)
	ls $(PYTHON_CLIENT_DIR)/wheelhouse/


bdist_manylinux_i686: ## Create 32 bits multilinux binary wheel distribution archives
	docker pull quay.io/pypa/manylinux1_i686
	docker run --rm -t -v $(REPO_ROOT):/io quay.io/pypa/manylinux1_i686 linux32 /io/.travis/build_wheels.sh
	ls wheelhouse/
	mkdir -p $(DIST_DIR)
	cp -v wheelhouse/* $(DIST_DIR)
	docker run --rm -t -v $(REPO_ROOT):/io quay.io/pypa/manylinux1_i686 linux32 /io/.travis/build_wheels_skyapi.sh
	mkdir -p $(PYTHON_CLIENT_DIR)/$(DIST_DIR)
	cp -v $(PYTHON_CLIENT_DIR)/wheelhouse/* $(PYTHON_CLIENT_DIR)/$(DIST_DIR)
	ls $(PYTHON_CLIENT_DIR)/wheelhouse/

dist: sdist bdist_wheel bdist_manylinux_amd64 ## Create distribution archives

check-dist: dist ## Perform self-tests upon distributions archives
	docker run --rm -t -v $(REPO_ROOT):/io quay.io/pypa/manylinux1_i686 linux32 /io/.travis/check_wheels.sh

format: ## Format code that autopep8
	(cd $(LIBSWIG_PYSKYFIBER) && autopep8 --in-place --aggressive --aggressive --aggressive --aggressive ./tests/*.py)

lint: ## Linter to pylint
	(cd $(LIBSWIG_PYSKYFIBER) && pylint -E tests/*.py)
	yamllint -d relaxed .travis.yml
	
clean: #Clean all
	make -C $(SKYLIBC_DIR) clean-libc
	$(PYTHON_BIN) -m pip uninstall -y pyskycoin
	$(PYTHON_BIN) -m pip uninstall -y skyapi
	rm -rfv $(LIBSWIG_PYSKYFIBER)/tests/__pycache__
	rm -rfv $(LIBSWIG_PYSKYFIBER)/skycoin/__pycache__
	rm -rfv $(LIBSWIG_PYSKYFIBER)/skycoin/*.pyc
	rm -rfv $(LIBSWIG_PYSKYFIBER)/tests/*.pyc
	rm -rfv $(LIBSWIG_PYSKYFIBER)/tests/utils/*.pyc
	rm -rfv $(LIBSWIG_PYSKYFIBER)/tests/utils/__pycache__
	rm -rfv $(LIBSWIG_PYSKYFIBER)/*.so
	rm -rfv qemu_python_*
	rm -rfv lib/skyapi/skyapi/__pycache__
	rm -rfv lib/skyapi/skyapi/*.pyc
	rm -rfv lib/skyapi/skyapi/models/*.pyc
	rm -rfv lib/skyapi/skyapi/models/__pycache__
	rm -rfv lib/skyapi/skyapi/api/*.pyc
	rm -rfv lib/skyapi/skyapi/api/__pycache__
	rm -rfv lib/skyapi/test/__pycache__
	rm -rfv lib/skyapi/test/*.pyc
	rm -rfv $(LIBSWIG_PYSKYFIBER)/swig/pyskycoin_wrap.c
	rm -rfv $(LIBSWIG_PYSKYFIBER)/skycoin/skycoin.py
	$(PYTHON_BIN) $(LIBSWIG_PYSKYFIBER)/setup.py clean
	

help: ## List available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'