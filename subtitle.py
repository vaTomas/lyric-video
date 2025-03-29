import os
import srt
from typing import List


def get_subtitles(srt_file_path: str) -> List[srt.Subtitle]:
    """
    Reads an SRT file and returns a list of subtitles.

    Args:
        srt_file_path (str): The path to the SRT file.

    Returns:
        List[srt.Subtitle]: A list of srt.Subtitle objects.

    Raises:
        FileNotFoundError: If the SRT file is not found.
        UnicodeDecodeError: If the SRT file cannot be decoded with UTF-8.
        srt.SRTParseError: If the SRT file has parsing errors.
        OSError: For other file-related errors.
    """
    if not os.path.exists(srt_file_path):
        raise FileNotFoundError(f"File not found: {srt_file_path}")
    if not srt_file_path.endswith('.srt'):
        raise ValueError("Invalid file path. Expected a file with '.srt' extension.")

    try:
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            srt_data = file.read()
        return list(srt.parse(srt_data))

    except FileNotFoundError as e:
        raise FileNotFoundError(f"SRT file not found: {srt_file_path}") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Error decoding SRT file: {srt_file_path}. Ensure it's UTF-8 encoded.") from e
    except srt.SRTParseError as e:
        raise srt.SRTParseError(f"Error parsing SRT file: {srt_file_path}. Invalid SRT format.") from e
    except OSError as e:
        raise OSError(f"Error reading SRT file: {srt_file_path}. {e}") from e
    except Exception as e:
        raise Exception(f"An unexpected error occurred while processing {srt_file_path}: {e}") from e


def main():
    srt_path = 'test/subtitle.srt'
    subtitles = get_subtitles(srt_path)
    for subtitle in subtitles:
        print(subtitle.content)

if __name__ == "__main__":
    main()