import os
import subprocess
import json

def extract_audio(path: str, overwrite_existing: bool = False) -> str:
    """
    Given a media file path, returns:
      - the original path if the file is audio-only,
      - the extracted audio file's path if the file is video,
      - None if the file is neither audio nor video.
    
    For video files, audio is extracted using FFmpeg with copy mode (no re-encoding).
    """
    # First, probe the file using ffprobe to get stream information.
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        info = json.loads(probe.stdout)
    except Exception as e:
        print(f"Error probing file '{path}': {e}")
        return None

    streams = info.get("streams", [])
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    has_video = any(stream.get("codec_type") == "video" for stream in streams)
    
    if has_video:
        # Video file: extract audio (if audio exists) using FFmpeg.
        if not has_audio:
            print(f"File '{path}' is a video but has no audio stream.")
            return None
        base, _ = os.path.splitext(path)
        # Create an output filename. You can adjust the extension as needed.
        commands = []

        output_path = f"{base}_audio_extracted.mka"
        if os.path.exists(output_path) and not overwrite_existing:
            raise FileExistsError(f" File already exists: {output_path}")
        else:
            commands.append("-y")
        
        commands.extend(["-i", path, "-vn", "-acodec", "copy"])
        command = ["ffmpeg"] + commands + [output_path]
        try:
            subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            print(f"Extracted audio to '{output_path}'")
            return output_path
        except Exception as e:
            print(f"Error extracting audio from '{path}': {e}")
            return None
    elif has_audio:
        # Audio file: simply return the same path.
        return path
    else:
        # Neither video nor audio.
        return None


# Example usage:
def main():
    media_path = input("Enter the media file path: ").strip()
    result = extract_audio(media_path)
    if result:
        print(f"Result: {result}")
    else:
        print("No valid media (audio/video) stream found or error occurred.")


if __name__ == '__main__':
    main()
