# Namescan validator ![./resources/nmbrs_hibob.png](./resources/surfaid_namescan_64x64.png)

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Validate suppliers against namescan emerald API

[![asciicast](https://asciinema.org/a/N66A8Q2CA0MbbB8MfCRQmBhgN.svg)](https://asciinema.org/a/N66A8Q2CA0MbbB8MfCRQmBhgN)

## Usage

### 💻 Windows

Download the [latest version](https://github.com/SurfAid/namescan/releases) of the executable and run.
```shell
surfaid_namescan.exe
````
Note that startup may be slow if you run a virus scanner.

### 🍏 Mac

Download the [latest version](https://github.com/SurfAid/namescan/releases) of the executable and run:

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