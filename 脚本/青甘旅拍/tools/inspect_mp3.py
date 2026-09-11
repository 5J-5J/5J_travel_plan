"""Read MP3 source facts using only the standard library; no mood/beat inference."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def synchsafe(raw: bytes) -> int:
    value = 0
    for byte in raw:
        value = (value << 7) | (byte & 0x7F)
    return value


def read_tags(data: bytes) -> tuple[dict, int]:
    if data[:3] != b"ID3" or len(data) < 10:
        return {}, 0
    version = data[3]
    end = min(10 + synchsafe(data[6:10]), len(data))
    tags = {"id3v2_major_version": version}
    # Avoid misreading extended/unsynchronised tag layouts; header size remains useful.
    if version not in (3, 4) or data[5] & 0xC0:
        tags["text_tags_skipped"] = "unsupported tag layout"
        return tags, end
    cursor = 10
    names = {"TIT2": "title", "TPE1": "artist", "TALB": "album"}
    while cursor + 10 <= end:
        header = data[cursor:cursor + 10]
        if not header[0]:
            break
        key = header[:4].decode("ascii", errors="replace")
        size = synchsafe(header[4:8]) if version == 4 else int.from_bytes(header[4:8], "big")
        if size <= 0 or cursor + 10 + size > end:
            break
        body = data[cursor + 10:cursor + 10 + size]
        if key in names and body and header[8:10] == b"\0\0":
            encoding = {0: "latin1", 1: "utf-16", 2: "utf-16-be", 3: "utf-8"}.get(body[0])
            if encoding:
                tags[names[key]] = body[1:].decode(encoding, errors="replace").strip("\0")
        cursor += 10 + size
    return tags, end


def frame_header(data: bytes, pos: int):
    if pos + 4 > len(data):
        return None
    value = int.from_bytes(data[pos:pos + 4], "big")
    if value >> 21 != 0x7FF:
        return None
    version = (value >> 19) & 3
    layer = (value >> 17) & 3
    br_index = (value >> 12) & 15
    sr_index = (value >> 10) & 3
    if version == 1 or layer != 1 or br_index in (0, 15) or sr_index == 3:
        return None
    table = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320] if version == 3 else [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]
    rate = [44100, 48000, 32000][sr_index] // {3: 1, 2: 2, 0: 4}[version]
    kbps = table[br_index]
    samples = 1152 if version == 3 else 576
    size = (144000 if version == 3 else 72000) * kbps // rate + ((value >> 9) & 1)
    if pos + size > len(data):
        return None
    return {"bytes": size, "sample_rate_hz": rate, "bitrate_kbps": kbps, "samples": samples, "channels": 1 if (value >> 6) & 3 == 3 else 2}


def inspect(path: Path) -> dict:
    data = path.read_bytes()
    tags, pos = read_tags(data)
    frames = 0
    seconds = 0.0
    rates, bitrates, channels = Counter(), Counter(), Counter()
    resync_bytes = 0
    while pos + 4 <= len(data):
        if data[pos:pos + 3] == b"TAG" and len(data) - pos == 128:
            break
        header = frame_header(data, pos)
        if not header:
            pos += 1
            resync_bytes += 1
            continue
        # Confirm the first candidate against the following frame.
        if frames == 0 and frame_header(data, pos + header["bytes"]) is None:
            pos += 1
            resync_bytes += 1
            continue
        frames += 1
        seconds += header["samples"] / header["sample_rate_hz"]
        rates[header["sample_rate_hz"]] += 1
        bitrates[header["bitrate_kbps"]] += 1
        channels[header["channels"]] += 1
        pos += header["bytes"]
    if not frames:
        raise ValueError("No supported MPEG Layer III frame sequence found")
    return {
        "schema_version": 1,
        "source_file": "bgm/" + path.name,
        "file_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "embedded_tags": tags,
        "mpeg_layer_iii_frames": frames,
        "frame_duration_seconds": round(seconds, 6),
        "sample_rate_hz_by_frame_count": dict(rates),
        "bitrate_kbps_by_frame_count": dict(bitrates),
        "channels_by_frame_count": dict(channels),
        "unparsed_or_resync_bytes_after_id3": resync_bytes,
        "method": "MP3 frame header scan; audio was not decoded or listened to",
        "limitations": ["Frame duration is not adjusted for encoder delay or end padding.", "Embedded tags are file-supplied metadata, not external identity verification.", "No BPM, loudness, mood, lyric, or music section claims are made."],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
