# Namescan validator ![./resources/nmbrs_hibob.png](./resources/surfaid_namescan_64x64.png)

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Validate suppliers against namescan emerald API 

## Usage

###  💻 Windows

###  🍏 Mac 
Download the latest version of the installer and run.
```shell
xattr -d com.apple.quarantine surfaid_namescan
chmod u+x surfaid_namescan
./surfaid_namescan
````


In your terminal, run the following command:
```bash
surfaid_namescan --help
```

## Development instructions
Install
```shell
pipenv install --dev
```
Execute local cli
```shell
pipenv run cli --help
```
Run tests
```shell
pipven run validate
```