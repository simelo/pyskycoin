#!/bin/bash

set -ev

# Install some dependencies
brew update;
brew outdated pyenv || brew upgrade pyenv;
brew install pyenv-virtualenv;
brew install readline xz;
echo 'Creating swig@3.0.12 formula';
# cd "$(brew --repository)/Library/Taps/homebrew/homebrew-core";
# git show 42d31bba7772fb01f9ba442d9ee98b33a6e7a055:Formula/swig.rb | grep -v 'fails_with' > Formula/swig.rb;
# echo 'Installing swig@3.0.12 (3.0.12)';
# brew install swig || brew link --overwrite swig;

mkdir swig_build && \
  cd swig_build && \
  curl -sL -o "swig-3.0.12.tar.gz" http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz && \
  tar -zxf swig-3.0.12.tar.gz && \
  cd swig-3.0.12 && \
  sudo ./configure --disable-dependency-tracking --prefix=/usr && \
  make && \
  make install && \
  cd ../../ && \
  rm -rf swig_build
  
brew install gimme;
brew install yamllint;

# Install Python
pyenv install ${PYTHON}
pyenv global ${PYTHON}

# Prepare and initialize pyenv environment
eval "$(pyenv init -)";
eval "$(pyenv virtualenv-init -)";
pyenv rehash

# Setup environment and PATH in MacOS
export PYCMD_VERSION="$(echo ${PYTHON} | cut -d . -f 1,2)"
export PYCMD_PATH="$(pyenv which python${PYCMD_VERSION})"
export PYCMD_DIRPATH="$( dirname ${PYCMD_PATH} )"
export PATH="${PYCMD_DIRPATH}:/Users/travis/.pyenv/shims:${PATH}"

eval "python${PYCMD_VERSION} -m pip install setuptools_scm"
eval "python${PYCMD_VERSION} -m pip install --upgrade pip setuptools wheel tox tox-pyenv pytest pytest-runner pylint autopep8"

