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

type ``vidtoolz beats --help`` to get help

### Usage Examples

```bash
# Detect beats from an audio file
vidtoolz beats my_song.mp3

# Detect beats with an offset (e.g., skip first 2 seconds)
vidtoolz beats my_song.mp3 --offset 2.0

# Save results to a custom file
vidtoolz beats my_song.mp3 --output beats.txt
```

### Options

- `audio` (required): Path to the audio file (mp3 or other format)
- `-of`, `--offset` (optional): Offset for music in seconds, default 0.0
- `-o`, `--output` (optional): Output path for the result, default is `beats.txt`



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
