import pytest
import vidtoolz_beats as w
import numpy as np
from scipy.io.wavfile import write as write_wav

from argparse import Namespace, ArgumentParser


def create_test_audio(filename, sr=22050, duration=5, freq=440.0):
    """Generate a simple test audio file (wav)."""
    t = np.linspace(0.0, duration, int(sr * duration), endpoint=False)
    data = 0.5 * np.sin(2 * np.pi * freq * t)
    write_wav(filename, sr, (data * 32767).astype(np.int16))


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


def test_detect_beats(tmpdir):
    """Test the detect_beats function."""
    audio_file = tmpdir.join("test.wav")
    create_test_audio(str(audio_file))

    beats_info = w.detect_beats(str(audio_file))

    assert isinstance(beats_info, np.ndarray)
    assert beats_info.shape[1] == 2
    assert np.all(beats_info[:, 0] >= 0)
    assert np.all((beats_info[:, 1] >= 0) & (beats_info[:, 1] <= 1))


def test_detect_beats_no_beats(tmpdir):
    """Test detect_beats with a silent audio file."""
    audio_file = tmpdir.join("silent.wav")
    # Create a silent audio file
    write_wav(str(audio_file), 22050, np.zeros(22050 * 5, dtype=np.int16))

    beats_info = w.detect_beats(str(audio_file))

    assert isinstance(beats_info, np.ndarray)
    assert beats_info.shape == (0, 2)


def test_run(tmpdir):
    """Test the run function."""
    audio_file = tmpdir.join("test.wav")
    output_file = tmpdir.join("beats.txt")
    create_test_audio(str(audio_file))

    args = Namespace(audio=str(audio_file), output=str(output_file))
    w.beats_plugin.run(args)

    assert output_file.exists()
    with open(str(output_file), "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        for line in lines:
            parts = line.strip().split(" ")
            assert len(parts) == 2
            assert float(parts[0]) >= 0
            assert 0 <= float(parts[1]) <= 1
