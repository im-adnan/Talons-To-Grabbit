#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import re

def sanitize_filename(title: str, ext: str) -> str:
    # Replace illegal/disruptive path characters
    clean = re.sub(r'[/\\?%*:|"<>!]', '-', title).strip()
    clean = re.sub(r'\s+', ' ', clean)
    if not clean:
        clean = "download"
    clean_ext = ext.lstrip('.').lower()
    if clean.lower().endswith(f".{clean_ext}"):
        return clean
    return f"{clean}.{clean_ext}"

def extract_media(url: str, resolution: str = "Best Quality"):
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    ytdlp_dir = os.path.join(plugin_dir, "yt-dlp")
    ytdlp_bin = os.path.join(plugin_dir, "yt-dlp")
    
    env = os.environ.copy()
    if os.path.isdir(ytdlp_dir):
        env["PYTHONPATH"] = f"{ytdlp_dir}:{env.get('PYTHONPATH', '')}"
        cmd = [
            sys.executable or "python3",
            "-m",
            "yt_dlp",
            "--no-warnings",
            "-q",
            "--dump-json",
            "--no-playlist",
            "--",
            url
        ]
    elif os.path.isfile(ytdlp_bin) and os.access(ytdlp_bin, os.X_OK):
        cmd = [
            ytdlp_bin,
            "--no-warnings",
            "-q",
            "--dump-json",
            "--no-playlist",
            "--",
            url
        ]
    else:
        # Fallback to system yt-dlp / yt_dlp
        cmd = [
            sys.executable or "python3",
            "-m",
            "yt_dlp",
            "--no-warnings",
            "-q",
            "--dump-json",
            "--no-playlist",
            "--",
            url
        ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        stdout, stderr = proc.communicate()
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute yt-dlp: {str(e)}"}

    if not stdout or not stdout.strip():
        err_msg = stderr.strip() if stderr else "No output from yt-dlp"
        return {"status": "error", "message": err_msg}

    # Slice JSON boundaries to ignore any residual non-fatal log lines
    try:
        first_brace = stdout.find("{")
        last_brace = stdout.rfind("}")
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON object found in output")
        raw_json = stdout[first_brace:last_brace + 1]
        data = json.loads(raw_json)
    except Exception as e:
        return {"status": "error", "message": f"Failed to parse yt-dlp metadata: {str(e)}"}

    title = data.get("title", "Video")
    thumbnail = data.get("thumbnail", "")
    raw_formats = data.get("formats", [])

    if not raw_formats:
        # Check if direct url is provided at top-level
        direct_url = data.get("url")
        if direct_url:
            ext = data.get("ext", "mp4")
            filename = sanitize_filename(title, ext)
            return {
                "status": "success",
                "title": title,
                "url": direct_url,
                "filename": filename,
                "ext": ext,
                "resolution": resolution,
                "thumbnail": thumbnail
            }
        return {"status": "error", "message": "No playable formats found in media metadata"}

    # Filter for direct HTTPS downloadable streams (exclude HLS m3u8 and DASH mpd playlists)
    direct_formats = []
    for f in raw_formats:
        f_url = f.get("url", "")
        if not f_url:
            continue
        proto = str(f.get("protocol", "")).lower()
        if "m3u8" in proto or ".m3u8" in f_url or "manifest/hls" in f_url or ".mpd" in f_url:
            continue
        direct_formats.append(f)

    if not direct_formats:
        direct_formats = raw_formats

    is_audio_only = (resolution.strip().lower() == "audio only")
    chosen_format = None
    chosen_ext = "m4a" if is_audio_only else "mp4"

    if is_audio_only:
        # Filter audio-only streams
        audio_formats = []
        for f in direct_formats:
            acodec = str(f.get("acodec", "none")).lower()
            vcodec = str(f.get("vcodec", "none")).lower()
            if acodec not in ["none", ""] and vcodec in ["none", ""]:
                audio_formats.append(f)

        def audio_sort_key(f):
            ext = str(f.get("ext", "")).lower()
            # Prioritize Apple/macOS native audio containers (m4a, mp3, aac)
            apple_score = 1 if ext in ["m4a", "mp3", "aac"] else 0
            abr = float(f.get("abr") or f.get("tbr") or 0.0)
            return (apple_score, abr)

        audio_formats.sort(key=audio_sort_key, reverse=True)
        chosen_format = audio_formats[0] if audio_formats else None

        if not chosen_format:
            # Fallback to any stream containing audio
            with_audio = [f for f in direct_formats if str(f.get("acodec", "none")).lower() not in ["none", ""]]
            chosen_format = with_audio[-1] if with_audio else direct_formats[0]

        ext = str(chosen_format.get("ext", "")).lower()
        if ext in ["mp4", "m4a"]:
            chosen_ext = "m4a"
        elif ext == "mp3":
            chosen_ext = "mp3"
        elif ext in ["webm", "opus"]:
            chosen_ext = "opus"
        else:
            chosen_ext = ext or "m4a"

    else:
        # Video requested
        requested_height = None
        for h in [2160, 1440, 1080, 720, 480, 360, 240, 144]:
            if str(h) in resolution:
                requested_height = h
                break

        video_formats = []
        for f in direct_formats:
            vcodec = str(f.get("vcodec", "none")).lower()
            note = str(f.get("format_note", "")).lower()
            if vcodec not in ["none", ""] and "storyboard" not in note:
                video_formats.append(f)

        if not video_formats:
            video_formats = direct_formats

        def parse_height(f):
            try:
                return int(f.get("height") or 0)
            except (ValueError, TypeError):
                return 0

        def parse_bitrate(f):
            try:
                return float(f.get("tbr") or f.get("vbr") or 0.0)
            except (ValueError, TypeError):
                return 0.0

        if requested_height:
            under_or_equal = [f for f in video_formats if parse_height(f) <= requested_height]
            pool = under_or_equal if under_or_equal else video_formats
            
            def height_sort_key(f):
                h = parse_height(f)
                has_audio = 1 if str(f.get("acodec", "none")).lower() not in ["none", ""] else 0
                is_mp4 = 1 if str(f.get("ext", "")).lower() == "mp4" else 0
                bitrate = parse_bitrate(f)
                return (h, has_audio, is_mp4, bitrate)

            pool.sort(key=height_sort_key, reverse=True)
            chosen_format = pool[0]
        else:
            # Best Quality: highest height, prefer mp4 and progressive audio
            def best_sort_key(f):
                h = parse_height(f)
                is_mp4 = 1 if str(f.get("ext", "")).lower() == "mp4" else 0
                has_audio = 1 if str(f.get("acodec", "none")).lower() not in ["none", ""] else 0
                bitrate = parse_bitrate(f)
                return (h, is_mp4, has_audio, bitrate)

            video_formats.sort(key=best_sort_key, reverse=True)
            chosen_format = video_formats[0]

        ext = str(chosen_format.get("ext", "")).lower()
        chosen_ext = ext if ext else "mp4"

    media_url = chosen_format.get("url")
    if not media_url:
        return {"status": "error", "message": "Failed to resolve direct playable stream URL"}

    actual_height = parse_height(chosen_format) if not is_audio_only else 0
    res_label = f"{actual_height}p" if actual_height > 0 else ("Audio Only" if is_audio_only else resolution)
    filename = sanitize_filename(title, chosen_ext)

    return {
        "status": "success",
        "title": title,
        "url": media_url,
        "filename": filename,
        "ext": chosen_ext,
        "resolution": res_label,
        "thumbnail": thumbnail
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: extractor.py <url> [resolution]"}))
        sys.exit(1)

    url = sys.argv[1]
    resolution = sys.argv[2] if len(sys.argv) > 2 else "Best Quality"

    result = extract_media(url, resolution)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
