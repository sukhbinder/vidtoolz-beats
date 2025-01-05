# vidtoolz-beats

[![PyPI](https://img.shields.io/pypi/v/vidtoolz-beats.svg)](https://pypi.org/project/vidtoolz-beats/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/vidtoolz-beats?include_prereleases&label=changelog)](https://github.com/sukhbinder/vidtoolz-beats/releases)
[![Tests](https://github.com/sukhbinder/vidtoolz-beats/workflows/Test/badge.svg)](https://github.com/sukhbinder/vidtoolz-beats/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/vidtoolz-beats/blob/main/LICENSE)

Get beats from a mp3 song

## Installation

First install [vidtoolz](https://github.com/sukhbinder/vidtoolz).

```bash
pip install vidtoolz
```

Then install this plugin in the same environment as your vidtoolz application.

```bash
vidtoolz install vidtoolz-beats
```
## Usage

type ``vidtoolz-beats --help`` to get help



## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd vidtoolz-beats
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
