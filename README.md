# Namescan validator ![./resources/nmbrs_hibob.png](./resources/surfaid_namescan_64x64.png)

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Validate suppliers against namescan emerald API

[![cli example](namescan.svg)](https://github.com/SurfAid/namescan/releases)

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

### Adjusting false positives logic

The logic marking matches as false positive and the rationale for doing so is [here](https://github.com/SurfAid/namescan/blob/821f5fa4667a50bc4fb0517d6702ea409e3c873b/models.py#L91)
and can be adjusted to your policy.