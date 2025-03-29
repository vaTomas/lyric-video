import os
import re
import subprocess
import sys

def parse_time(timestr: str) -> float:
    """Parses a time string in "HH:MM:SS,mmm" format and returns time in seconds."""
    hh, mm, ss_ms = timestr.split(":")
    ss, ms = ss_ms.split(",")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0

def parse_srt(srt_path: str) -> list:
    """
    Parses an SRT file and returns a list of (start, end) intervals in seconds.
    """
    intervals = []
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    entries = re.split(r'\n\s*\n', content.strip())
    for entry in entries:
        lines = entry.splitlines()
        if len(lines) >= 2:
            m = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', lines[1])
            if m:
                start_str, end_str = m.groups()
                start = parse_time(start_str)
                end = parse_time(end_str)
                intervals.append((start, end))
    return intervals

def build_effective_time_expr(intervals: list) -> str:
    """
    Builds an FFmpeg expression that computes effective time:
      te = t - ( sum over intervals of: if(t > s, if(t < e, t - s, e - s), 0) )
    """
    if not intervals:
        return "t"
    terms = []
    for (s, e) in intervals:
        # For each interval, if t > s then subtract either (t - s) if still within the interval, or (e - s) if after.
        term = f"if(gt(t,{s}), if(lt(t,{e}), t-{s}, {e}-{s}), 0)"
        terms.append(term)
    te_expr = f"t - ({' + '.join(terms)})"
    return te_expr

def process_media(jpg_path: str, srt_path: str, mka_path: str, output_path: str):
    """
    Processes the media by creating a video from a JPG image and background audio (MKA),
    applying a pan effect that moves the image only during periods when subtitles are NOT active.
    
    Parameters:
      jpg_path: Path to the input image (JPG).
      srt_path: Path to the subtitle file (SRT).
      mka_path: Path to the background music (MKA).
      output_path: Path for the generated video output (e.g., output.mp4).
    """
    # Parse SRT to get subtitle intervals
    intervals = parse_srt(srt_path)
    print("Subtitle intervals (seconds):", intervals)
    
    # Build the effective time expression
    te_expr = build_effective_time_expr(intervals)
    print("Effective time expression:", te_expr)
    
    pan_speed = 50  # pixels per effective second; adjust as needed
    # x_expr uses the effective time to compute horizontal offset, clamped so as not to exceed available width.
    x_expr = f"min({pan_speed}*({te_expr}), iw-ow)"
    
    # Build the FFmpeg filter_complex:
    #  - Loop the image (-loop 1)
    #  - Apply zoompan with our x offset expression (panning horizontally)
    #  - Set a fixed frame rate (fps=25) and output format.
    filter_complex = f"[0:v]zoompan=x='{x_expr}':y=0:fps=25:d=1,format=yuv420p[v]"
    
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", jpg_path,
        "-i", mka_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "1:a",
        "-c:a", "copy",
        "-shortest",
        output_path
    ]
    
    print("Running FFmpeg command:")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("Output video created at:", output_path)
    except subprocess.CalledProcessError as e:
        print("Error during FFmpeg processing:", e)

if __name__ == '__main__':
    import subprocess
    jpg_path = input("Enter path to the JPG image: ").strip()
    if not jpg_path:
        jpg_path = "test/image.jpg"
    srt_path = input("Enter path to the SRT file: ").strip()
    if not srt_path:
        srt_path = "test/subtitle.srt"
    mka_path = input("Enter path to the MKA audio file: ").strip()
    if not mka_path:
        mka_path = "test/audio.mka"
    output_path = input("Enter desired output video path (e.g., output.mp4): ").strip()
    if not output_path:
        output_path = "test/output.mp4"
    
    process_media(jpg_path, srt_path, mka_path, output_path)
