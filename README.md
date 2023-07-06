# Namescan validator ![./resources/nmbrs_hibob.png](./resources/surfaid_namescan_64x64.png)

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Validate suppliers against namescan emerald API 

## Usage

### <svg aria-label="macOS" class="octicon mr-2 color-fg-muted flex-shrink-0" width="16" height="16" viewBox="0 0 21 24" xmlns="http://www.w3.org/2000/svg"><path d="M19.971 18.7035C19.6173 19.5192 19.1811 20.2965 18.669 21.0233C17.9842 21.9908 17.424 22.6605 16.9912 23.0317C16.3215 23.6422 15.6037 23.955 14.8357 23.973C14.2845 23.973 13.6192 23.817 12.8452 23.502C12.0675 23.187 11.355 23.0317 10.7017 23.0317C10.017 23.0317 9.28275 23.1878 8.49675 23.502C7.71 23.817 7.07625 23.982 6.59175 23.9977C5.85525 24.0292 5.12175 23.7075 4.38675 23.0317C3.9195 22.6275 3.33525 21.9345 2.63175 20.952C1.88025 19.9035 1.2615 18.687 0.777 17.301C0.2595 15.8025 0 14.3535 0 12.9487C0 11.34 0.351 9.95325 1.05375 8.79C1.5864 7.87554 2.34651 7.11439 3.26025 6.5805C4.16398 6.04596 5.19234 5.75835 6.24225 5.7465C6.828 5.7465 7.59525 5.92575 8.5485 6.27825C9.4995 6.63225 10.1107 6.81075 10.3785 6.81075C10.5787 6.81075 11.2575 6.60075 12.4072 6.183C13.4947 5.79525 14.4127 5.6355 15.1635 5.697C17.2005 5.8605 18.7312 6.6555 19.7497 8.0895C17.9272 9.1845 17.0257 10.716 17.0437 12.6818C17.0602 14.214 17.6212 15.4875 18.7222 16.4993C19.2104 16.9619 19.779 17.3315 20.4 17.5897C20.2635 17.9775 20.1217 18.348 19.971 18.7035V18.7035ZM15.2985 0.4815C15.2985 1.6815 14.856 2.80275 13.9732 3.84C12.909 5.07225 11.622 5.78475 10.2262 5.67225C10.2073 5.52124 10.1978 5.36919 10.1977 5.217C10.1977 4.065 10.7047 2.832 11.6025 1.82325C12.051 1.3125 12.6225 0.88875 13.314 0.54975C14.0047 0.216 14.658 0.03 15.2722 0C15.2902 0.16125 15.2977 0.3225 15.2977 0.4815H15.2985Z"></path></svg> Windows

### <svg aria-label="Windows" class="octicon mr-2 color-fg-muted flex-shrink-0" width="16" height="16" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"> <g clip-path="url(#clip0)"><path d="M0.001 4.53L13.08 2.756L13.085 15.331L0.015 15.406L0 4.53H0.001ZM13.072 16.78L13.082 29.366L0.012 27.574L0.01 16.695L13.071 16.779L13.072 16.78ZM14.658 2.523L31.998 0V15.17L14.658 15.308V2.523ZM32 16.898L31.997 32L14.657 29.56L14.633 16.87L32.001 16.898H32Z"></path></g><defs><clipPath id="clip0"><rect width="32" height="32" fill="white"></rect></clipPath></defs></svg> Windows 

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