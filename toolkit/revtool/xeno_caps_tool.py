#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xeno_caps_tool.py — Xenoblade-style caption unpack/repack tool

Features
- Unpack binary captions into TXT (CP932/SJIS) with a heuristic for first line without time.
- Repack TXT back into the original binary layout.
- TXT format is line-based: "TIME_HEX<TAB>TEXT". Use "[CLEAR]" to emit an empty line (just the 0x00 terminator).

Heuristic for first record without time:
- If the file begins with bytes that look like a valid CP932 lead+trail pair, the first record is parsed
  as text until 0x00 with an implicit time value of 0x0000.
- Otherwise, the first two bytes are treated as a big-endian 16-bit time.

Usage
------
Unpack:
  python xeno_caps_tool.py unpack input.bin output.txt --encoding cp932

Repack:
  python xeno_caps_tool.py repack input.txt output.bin --encoding cp932

Optional:
  --fps 30  # prints time in seconds during unpack (info only; TXT still stores hex frames)

TXT Format
----------
One record per line:
    TIME_HEX<TAB>TEXT

Examples:
    0000\t遙か昔
    00D9\t[CLEAR]
    0104\tこの世界がまだ

Notes
-----
- Encoding default is cp932 (Windows-31J). This generally preserves characters like '遙' better than Python's 'shift_jis' codec.
- Repacker writes 2-byte big-endian times, CP932-encoded strings, and a single 0x00 terminator for each record.
"""

import argparse
from typing import List, Dict, Tuple

def is_cp932_lead(b: int) -> bool:
    return (0x81 <= b <= 0x9F) or (0xE0 <= b <= 0xFC)

def is_cp932_trail(b: int) -> bool:
    return (0x40 <= b <= 0x7E) or (0x80 <= b <= 0xFC)

def unpack_records(data: bytes, encoding: str = "cp932") -> List[Dict]:
    """Unpack binary data into a list of records with keys:
       index, time_hex, time_dec, type ('LINE'|'CLEAR'), text, raw_len.
       Applies the 'first line may have no time' heuristic.
    """
    n = len(data)
    pos = 0
    idx = 0
    rows: List[Dict] = []

    def read_u16_be(offset: int) -> Tuple[int, int]:
        if offset + 2 > n:
            return None, offset
        return int.from_bytes(data[offset:offset+2], "big"), offset + 2

    # Heuristic: first record might be pure text (no initial time field)
    if n >= 2 and is_cp932_lead(data[0]) and is_cp932_trail(data[1]):
        # parse text until 0x00
        start = 0
        pos = 0
        while pos < n and data[pos] != 0x00:
            pos += 1
        chunk = data[start:pos]
        if pos < n and data[pos] == 0x00:
            pos += 1
        text = chunk.decode(encoding, errors="replace") if chunk else ""
        rows.append({
            "index": idx,
            "time_hex": f"{0:04X}",
            "time_dec": 0,
            "type": "LINE" if text else "CLEAR",
            "text": text,
            "raw_len": len(chunk),
        })
        idx += 1

    # Continue parsing normal [time][string][0x00] entries
    while pos < n:
        t, pos = read_u16_be(pos)
        if t is None:
            break
        # read until 0x00
        start = pos
        while pos < n and data[pos] != 0x00:
            pos += 1
        chunk = data[start:pos]
        if pos < n and data[pos] == 0x00:
            pos += 1
        if chunk:
            text = chunk.decode(encoding, errors="replace")
            kind = "LINE"
        else:
            text = ""
            kind = "CLEAR"
        rows.append({
            "index": idx,
            "time_hex": f"{t:04X}",
            "time_dec": t,
            "type": kind,
            "text": text,
            "raw_len": len(chunk),
        })
        idx += 1
    return rows

def export_txt(rows: List[Dict], out_path: str, encoding: str = "cp932"):
    with open(out_path, "w", encoding=encoding, errors="replace") as out:
        for r in rows:
            text = r["text"] if r["text"] else "[CLEAR]"
            out.write(f"{r['time_hex']}\t{text}\n")

def repack_from_txt(txt_path: str, out_path: str, encoding: str = "cp932"):
    out = bytearray()
    with open(txt_path, "r", encoding=encoding, errors="strict") as f:
        for line_no, line in enumerate(f, 1):
            line = line.rstrip("\r\n")
            if not line:
                continue
            # split once on tab; fall back to first space
            if "\t" in line:
                time_hex, text = line.split("\t", 1)
            else:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    time_hex, text = parts
                else:
                    raise ValueError(f"Line {line_no}: expected 'TIME\\tTEXT', got: {line}")
            try:
                time_val = int(time_hex, 16)
            except ValueError:
                raise ValueError(f"Line {line_no}: invalid TIME_HEX '{time_hex}'")
            out += time_val.to_bytes(2, "big")
            if text == "[CLEAR]":
                out += b"\x00"
            else:
                out += text.encode(encoding, errors="strict")
                out += b"\x00"
    with open(out_path, "wb") as o:
        o.write(out)

def run_unpack(args):
    data = open(args.input, "rb").read()
    rows = unpack_records(data, encoding=args.encoding)
    export_txt(rows, args.output, encoding=args.encoding)
    if args.fps:
        # Just an info print to STDOUT; the TXT still uses frames in hex.
        print(f"[info] Unpacked {len(rows)} records. Example time conversions at {args.fps} fps:")
        for r in rows[:5]:
            sec = r["time_dec"] / args.fps
            print(f"  {r['time_hex']} -> {r['time_dec']} frames -> {sec:.3f} s")
    print(f"Unpacked -> {args.output} (encoding={args.encoding})")

def run_repack(args):
    repack_from_txt(args.input, args.output, encoding=args.encoding)
    print(f"Repacked -> {args.output} (encoding={args.encoding})")

def main():
    ap = argparse.ArgumentParser(description="Unpack/Repack caption files (CP932/SJIS).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_unpack = sub.add_parser("unpack", help="Unpack BIN -> TXT")
    ap_unpack.add_argument("input", help="Input binary file")
    ap_unpack.add_argument("output", help="Output TXT file")
    ap_unpack.add_argument("--encoding", default="cp932", help="Text encoding (default: cp932)")
    ap_unpack.add_argument("--fps", type=float, default=None, help="Optional FPS for info conversion")
    ap_unpack.set_defaults(func=run_unpack)

    ap_repack = sub.add_parser("repack", help="Repack TXT -> BIN")
    ap_repack.add_argument("input", help="Input TXT file")
    ap_repack.add_argument("output", help="Output binary file")
    ap_repack.add_argument("--encoding", default="cp932", help="Text encoding (default: cp932)")
    ap_repack.set_defaults(func=run_repack)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
