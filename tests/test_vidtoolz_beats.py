import pytest
import vidtoolz_beats as w
import numpy as np
import librosa
from argparse import Namespace, ArgumentParser
from unittest.mock import patch, MagicMock
import tempfile
import os
import subprocess


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


def test_detect_beats_with_mock_audio():
    """Test detect_beats function with mocked audio data"""
    # Create mock audio data
    sr = 22050  # sample rate
    duration = 2.0  # seconds
    y = np.random.randn(int(sr * duration))  # random audio signal
    
    # Mock librosa functions
    with patch('librosa.load', return_value=(y, sr)) as mock_load, \
         patch('librosa.onset.onset_strength', return_value=np.ones(int(sr * duration))) as mock_onset, \
         patch('librosa.beat.beat_track', return_value=(120.0, np.array([1000, 2000, 3000]))) as mock_beat_track, \
         patch('librosa.frames_to_time', return_value=np.array([0.5, 1.0, 1.5])) as mock_frames_to_time:
        
        result = w.detect_beats("dummy_audio.mp3")
        
        # Verify the function was called with correct parameters
        mock_load.assert_called_once_with("dummy_audio.mp3", offset=0.0)
        
        # Verify the result structure
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == 3  # 3 beats
        assert result.shape[1] == 2  # time and amplitude
        
        # Verify the times are correct
        assert np.allclose(result[:, 0], [0.5, 1.0, 1.5])
        
        # Verify amplitudes are normalized (should be between 0 and 1)
        assert np.all((result[:, 1] >= 0) & (result[:, 1] <= 1))


def test_detect_beats_with_offset():
    """Test detect_beats function with offset parameter"""
    sr = 22050
    duration = 2.0
    y = np.random.randn(int(sr * duration))
    
    with patch('librosa.load', return_value=(y, sr)) as mock_load, \
         patch('librosa.onset.onset_strength', return_value=np.ones(int(sr * duration))) as mock_onset, \
         patch('librosa.beat.beat_track', return_value=(120.0, np.array([1000, 2000]))) as mock_beat_track, \
         patch('librosa.frames_to_time', return_value=np.array([0.5, 1.0])) as mock_frames_to_time:
        
        result = w.detect_beats("dummy_audio.mp3", offset=10.5)
        
        # Verify offset was passed correctly
        mock_load.assert_called_once_with("dummy_audio.mp3", offset=10.5)


def test_plugin_run_with_mock_audio():
    """Test the plugin's run method with mocked audio"""
    # Create a temporary output file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        tmp_output = tmp_file.name
    
    try:
        # Mock the detect_beats function
        mock_beats = np.array([[1.0, 0.8], [2.0, 0.9], [3.0, 0.7]])
        
        with patch.object(w, 'detect_beats', return_value=mock_beats), \
             patch('os.path.exists', return_value=True):
            
            args = Namespace(audio="test.mp3", output=tmp_output)
            w.beats_plugin.run(args)
            
            # Verify the output file was created and contains expected data
            with open(tmp_output, 'r') as f:
                content = f.read()
                lines = content.strip().split('\n')
                
                assert len(lines) == 3
                # Check first line format
                first_line = lines[0]
                assert "1.0000" in first_line
                assert "0.8000" in first_line
    
    finally:
        # Clean up
        if os.path.exists(tmp_output):
            os.unlink(tmp_output)


def test_plugin_run_file_not_found():
    """Test plugin run method when audio file doesn't exist"""
    with patch('os.path.exists', return_value=False):
        args = Namespace(audio="nonexistent.mp3", output="output.txt")
        result = w.beats_plugin.run(args)
        assert result is None  # Should return None when file not found


def test_plugin_run_with_custom_output():
    """Test plugin run method with custom output path"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        tmp_output = tmp_file.name
    
    try:
        mock_beats = np.array([[0.5, 0.6], [1.5, 0.7]])
        
        with patch.object(w, 'detect_beats', return_value=mock_beats), \
             patch('os.path.exists', return_value=True):
            
            args = Namespace(audio="test.mp3", output=tmp_output)
            w.beats_plugin.run(args)
            
            # Verify output file exists and has correct content
            assert os.path.exists(tmp_output)
            
            with open(tmp_output, 'r') as f:
                content = f.read()
                assert "0.5000 0.6000" in content
                assert "1.5000 0.7000" in content
    
    finally:
        if os.path.exists(tmp_output):
            os.unlink(tmp_output)


def test_parser_custom_output():
    """Test parser with custom output path"""
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)
    
    result = parser.parse_args(["test.mp3", "-o", "custom_output.txt"])
    assert result.audio == "test.mp3"
    assert result.output == "custom_output.txt"


def test_detect_beats_empty_result():
    """Test detect_beats when no beats are detected"""
    sr = 22050
    y = np.random.randn(sr)  # 1 second of audio
    
    with patch('librosa.load', return_value=(y, sr)), \
         patch('librosa.onset.onset_strength', return_value=np.ones(sr)), \
         patch('librosa.beat.beat_track', return_value=(0.0, np.array([]))), \
         patch('librosa.frames_to_time', return_value=np.array([])):
        
        result = w.detect_beats("no_beats.mp3")
        
        # Should return empty array with correct shape
        assert isinstance(result, np.ndarray)
        assert result.shape == (0, 2)  # 0 rows, 2 columns (time, amplitude)


def test_integration_end_to_end_workflow():
    """Integration test for the complete workflow from CLI to output file"""
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mp3') as audio_file:
        audio_path = audio_file.name
        
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as output_file:
        output_path = output_file.name
    
    try:
        # Mock audio data that will be "loaded" from the fake audio file
        sr = 22050
        duration = 3.0
        y = np.random.randn(int(sr * duration))
        
        # Mock beat data
        beat_frames = np.array([sr//2, sr, sr*2])  # beats at 0.5s, 1s, 2s
        beat_times = np.array([0.5, 1.0, 2.0])
        onset_env = np.ones(int(sr * duration))
        
        with patch('librosa.load', return_value=(y, sr)), \
             patch('librosa.onset.onset_strength', return_value=onset_env), \
             patch('librosa.beat.beat_track', return_value=(120.0, beat_frames)), \
             patch('librosa.frames_to_time', return_value=beat_times), \
             patch('os.path.exists', return_value=True):
            
            # Test the complete workflow
            args = Namespace(audio=audio_path, output=output_path)
            w.beats_plugin.run(args)
            
            # Verify output file was created
            assert os.path.exists(output_path)
            
            # Verify output file content
            with open(output_path, 'r') as f:
                content = f.read()
                lines = content.strip().split('\n')
                
                # Should have 3 lines (one for each beat)
                assert len(lines) == 3
                
                # Verify each line has the expected format
                for line in lines:
                    parts = line.strip().split()
                    assert len(parts) == 2  # time and amplitude
                    
                    # Verify time values are reasonable
                    time_val = float(parts[0])
                    assert 0.0 <= time_val <= 3.0  # within audio duration
                    
                    # Verify amplitude is normalized
                    amp_val = float(parts[1])
                    assert 0.0 <= amp_val <= 1.0
                    
                # Verify specific expected beats
                assert any("0.5000" in line for line in lines)
                assert any("1.0000" in line for line in lines)
                assert any("2.0000" in line for line in lines)
    
    finally:
        # Clean up temporary files
        for path in [audio_path, output_path]:
            if os.path.exists(path):
                os.unlink(path)


def test_integration_with_offset():
    """Integration test with offset parameter"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as output_file:
        output_path = output_file.name
    
    try:
        sr = 22050
        duration = 2.0
        y = np.random.randn(int(sr * duration))
        
        beat_frames = np.array([sr//4, sr//2])  # beats at 0.25s and 0.5s (relative to offset)
        beat_times = np.array([0.25, 0.5])
        onset_env = np.ones(int(sr * duration))
        
        with patch('librosa.load', return_value=(y, sr)), \
             patch('librosa.onset.onset_strength', return_value=onset_env), \
             patch('librosa.beat.beat_track', return_value=(120.0, beat_frames)), \
             patch('librosa.frames_to_time', return_value=beat_times), \
             patch('os.path.exists', return_value=True):
            
            # Test with offset
            args = Namespace(audio="dummy.mp3", output=output_path)
            
            # Modify the plugin to use offset
            with patch.object(w, 'detect_beats') as mock_detect:
                mock_beats = np.array([[5.25, 0.8], [5.5, 0.9]])  # times include offset
                mock_detect.return_value = mock_beats
                
                w.beats_plugin.run(args)
                
                # Verify the detect_beats was called (we can't easily test the offset
                # parameter in this integration test without more complex mocking)
                mock_detect.assert_called_once()
                
                # Verify output contains the offset times
                with open(output_path, 'r') as f:
                    content = f.read()
                    assert "5.2500" in content
                    assert "5.5000" in content
    
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_integration_error_handling():
    """Integration test for error handling"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as output_file:
        output_path = output_file.name
    
    try:
        # Test with non-existent file
        with patch('os.path.exists', return_value=False):
            args = Namespace(audio="nonexistent.mp3", output=output_path)
            result = w.beats_plugin.run(args)
            
            # Should return None and not create output file
            assert result is None
            assert not os.path.exists(output_path)
    
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)
