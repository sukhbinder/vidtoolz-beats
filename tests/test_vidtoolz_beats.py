import pytest
import vidtoolz_beats as w

from argparse import Namespace, ArgumentParser


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_args(["hello.mp3"])
    assert result.audio == "hello.mp3"
    assert result.output == "beats.txt"


def test_plugin(capsys):
    w.beats_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``vidtoolz`` plugin." in captured.out
