import vidtoolz
import librosa
import os


def detect_beats(audio_file):
    """
    Detect major beats in an audio file and return their time and normalized amplitude.

    Parameters:
        audio_file (str): Path to the audio file.

    Returns:
        List[Tuple[float, float]]: A list of tuples where each tuple contains:
            - Time of the beat (in seconds)
            - Normalized amplitude of the beat (0 to 1)
    """
    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Detect onset strengths
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # Detect beat times using onset strengths
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset_env)

    # Convert beat frame indices to time (in seconds)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Normalize the amplitude of onset strengths to [0, 1]
    normalized_amplitudes = onset_env[beat_frames] / np.max(onset_env)

    # Combine beat times and normalized amplitudes
    beats_info = list(zip(beat_times, normalized_amplitudes))

    return beats_info


def create_parser(subparser):
    parser = subparser.add_parser("beats", description="Get beats from a mp3 song")
    parser.add_argument("audio", type=str, help="Path to the audio file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="beats.txt",
        help="Output path for the result",
    )
    return parser


class ViztoolzPlugin:
    """ Get beats from a mp3 song """

    __name__ = "beats"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        if not os.path.exists(args.audio):
            print(f"Error: Audio file '{args.audio}' not found.")
            return

        beats_info = detect_beats(args.audio)

        with open(args.output, "w") as f:
            for beat in beats_info:
                time, amplitude = beat
                f.write(f"{time:.4f} {amplitude:.4f}\n")

    def hello(self, args):
        # this routine will be called when "vidtoolz "beats is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


beats_plugin = ViztoolzPlugin()
