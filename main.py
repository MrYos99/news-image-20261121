#!/usr/bin/env python3
"""news-image-20261121 entry: write the composed front page to /output.

The front page is composed at build time (compose.py) and held in this
repository as entry.png. The grader runs this program with no network
and standard library only, so all it does is check the image (format,
dimensions, size cap) and copy it unchanged. Deterministic: the same
input bytes give the same output bytes on every run.
"""
import hashlib
import os
import struct
import sys

WANT_W, WANT_H = 1024, 1024
MAX_BYTES = 1_048_576


def jpeg_size(data):
    """Walk JPEG markers to the frame header; return (w, h) or None."""
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h = struct.unpack(">H", data[i + 5:i + 7])[0]
            w = struct.unpack(">H", data[i + 7:i + 9])[0]
            return w, h
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        size = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + size
    return None


def png_size(data):
    if len(data) < 33 or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def check(data):
    """Return (format, w, h); exit with a message on any failure."""
    if len(data) > MAX_BYTES:
        sys.exit(f"entry image is {len(data)} bytes, over the 1 MiB cap")
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        kind, dims = "PNG", png_size(data)
    elif data[:3] == b"\xff\xd8\xff":
        kind, dims = "JPEG", jpeg_size(data)
    else:
        sys.exit("entry image is neither PNG nor JPEG (bad magic bytes)")
    if dims is None:
        sys.exit(f"could not read {kind} dimensions")
    w, h = dims
    if (w, h) != (WANT_W, WANT_H):
        sys.exit(f"entry image is {w}x{h}, expected {WANT_W}x{WANT_H}")
    return kind, w, h


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.png"), "rb") as fh:
        data = fh.read()
    kind, w, h = check(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)

    with open(dst, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        sys.exit("output differs from source after copy")
    check(written)
    print(f"wrote {dst}: {kind} {w}x{h}, {len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()[:16]}...")


if __name__ == "__main__":
    main()
