import argparse
import os
import sys


def _apply_name_suffix(path, new_name_suffix):
    """
    Adds a suffix to the name of a file.
    _add_name_suffix("/path/to/file.ext", "_left") -> "/path/to/file_left.ext"
    """
    name, ext = os.path.splitext(path)
    return f"{name}{new_name_suffix}{ext}"


def _apply_ext(path, new_ext):
    """
    Sets the extension of a file.
    _apply_ext("/path/to/file.ext", ".wav") -> "/path/to/file.wav"
    """
    name, _ = os.path.splitext(path)
    return f"{name}{new_ext}"


def _print_file_exists(path):
    if os.path.exists(path):
        print(f"Generated {path}")
    else:
        print(f"WARNING: failed to generate {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Print video durations\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("vidfile", help="Path to vid file", nargs="?")
    parser.add_argument("outwavfile", help="Path to output wav file", nargs="?")
    args = parser.parse_args()
    path = args.vidfile or input("in vid file: ")
    out_wav = args.outwavfile or path
    out_wav = _apply_ext(out_wav, ".wav")
    if not os.path.exists(path):
        print(f"{path} does not exist")
        sys.exit(1)
    out_left_path = _apply_name_suffix(out_wav, "_left")
    out_right_path = _apply_name_suffix(out_wav, "_right")
    cmd0 = f'static_ffmpeg -y -i "{path}" -filter_complex "[0:a]channelsplit=channel_layout=stereo:channels=FR[right]" -map "[right]" "{out_right_path}"'
    cmd1 = f'static_ffmpeg -y -i "{path}" -filter_complex "[0:a]channelsplit=channel_layout=stereo:channels=FL[left]" -map "[left]" "{out_left_path}"'
    print(f"Executing:\n  {cmd0}\n")
    os.system(cmd0)
    print(f"Executing:\n  {cmd1}\n")
    os.system(cmd1)
    print("\nDone\n")
    _print_file_exists(out_right_path)
    _print_file_exists(out_left_path)


if __name__ == "__main__":
    main()
