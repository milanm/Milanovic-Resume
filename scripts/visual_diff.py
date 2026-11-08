#!/usr/bin/env python3
"""Catch layout changes nobody meant to make: compare page 1 of each PDF with a stored render.

The text checks pass when spacing breaks, a rule disappears or a heading moves. This
script renders page 1 of every PDF in pdf/ at low resolution, compares it pixel by pixel
with tests/visual/<name>.png and fails when more than --threshold of the page differs.
A changed word stays under the threshold; a spacing or layout change does not.

Each comparison writes build/visual/<name>.png (the new render) and, when it fails,
build/visual/<name>-diff.png with the changed pixels in red.

Usage:
  python3 scripts/visual_diff.py                 # compare
  python3 scripts/visual_diff.py --update        # accept the current renders as the new baseline

Renders differ slightly between poppler and font versions, so make baselines on the
machine that runs the check. CI uploads its renders as an artifact for that.
Needs: poppler-utils, pip install pillow
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "tests" / "visual"
OUT = ROOT / "build" / "visual"
DPI = 50
LEVEL = 64  # a pixel counts as changed when its grey value moves by more than this


def render(pdf):
    stem = OUT / pdf.stem
    subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png", "-singlefile", "-f", "1", "-l", "1",
                    str(pdf), str(stem)], check=True)
    return stem.with_suffix(".png")


def compare(new, old):
    a, b = Image.open(new).convert("L"), Image.open(old).convert("L")
    if a.size != b.size:
        return 1.0, None
    diff = ImageChops.difference(a, b).point(lambda v: 255 if v > LEVEL else 0)
    changed = diff.histogram()[255]
    return changed / (a.size[0] * a.size[1]), diff


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdfs", nargs="*", help="default: every PDF in pdf/")
    ap.add_argument("--threshold", type=float, default=0.005, help="share of changed pixels that fails (default 0.5%%)")
    ap.add_argument("--update", action="store_true", help="copy the new renders to tests/visual/")
    args = ap.parse_args()

    pdfs = [Path(p) for p in args.pdfs] or sorted((ROOT / "pdf").glob("*.pdf"))
    OUT.mkdir(parents=True, exist_ok=True)
    failed = 0
    for pdf in pdfs:
        new = render(pdf)
        old = BASE / new.name
        if args.update:
            BASE.mkdir(parents=True, exist_ok=True)
            shutil.copy(new, old)
            print(f"baseline {old.relative_to(ROOT)}")
            continue
        if not old.exists():
            print(f"FAIL {pdf.name}: no baseline at {old.relative_to(ROOT)} (run with --update)")
            failed += 1
            continue
        share, diff = compare(new, old)
        if share > args.threshold:
            failed += 1
            print(f"FAIL {pdf.name}: {share:.2%} of the page changed (limit {args.threshold:.2%})")
            if diff is not None:
                overlay = Image.open(new).convert("RGB")
                overlay.paste((220, 0, 0), mask=diff)
                overlay.save(OUT / f"{pdf.stem}-diff.png")
            else:
                print("     page size changed")
        else:
            print(f"PASS {pdf.name}: {share:.2%} changed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
