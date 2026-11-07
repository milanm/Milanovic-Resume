#!/usr/bin/env python3
"""Check a resume PDF the way an applicant tracking system (ATS) would read it.

Uses poppler's pdfinfo and pdftotext (poppler-utils). With --parser pdfminer it also
reads the text with pdfminer.six (pip install pdfminer.six), a parser that ignores the
ActualText hints some PDF writers add, so it is the stricter of the two.

Checks:
  1. Page count: one page by default ("One page. Period.").
  2. Text exists: at least --min-words words come out (a blank or image-only PDF fails).
  3. Text layer: every character a parser extracts is the character you typed.
     Fails on ligature glyphs (U+FB00-FB06), replacement characters (U+FFFD),
     private-use glyphs and look-alike hyphens (U+2010, U+2011) that break keyword search.
  4. Reading order: the strings passed to --expect come out in that order.
  5. Required strings: e.g. your email survives extraction intact.

Usage:
  python3 scripts/check_pdf.py pdf/resume-latex.pdf --expect SKILLS "PROFESSIONAL EXPERIENCE" EDUCATION
  python3 scripts/check_pdf.py pdf/resume-typst.pdf --parser pdfminer --contains cloud-native
"""
import argparse
import subprocess
import sys

BAD_CHARS = {
    **{chr(c): "ligature glyph" for c in range(0xFB00, 0xFB07)},
    "�": "replacement character",
    "‐": "Unicode hyphen (U+2010), keyword search for '-' will miss it",
    "‑": "non-breaking hyphen (U+2011), keyword search for '-' will miss it",
    "­": "soft hyphen",
}


def run(*cmd):
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8").stdout
    except FileNotFoundError:
        sys.exit(f"'{cmd[0]}' not found. Install poppler-utils (Linux), poppler (macOS: brew install poppler) "
                 "or the poppler binaries for Windows, then try again.")


def extract(pdf, parser):
    if parser == "pdfminer":
        try:
            from pdfminer.high_level import extract_text
        except ImportError:
            sys.exit("pdfminer.six is not installed: pip install pdfminer.six")
        return extract_text(pdf)
    return run("pdftotext", "-enc", "UTF-8", pdf, "-")


def page_count(pdf):
    for line in run("pdfinfo", pdf).splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise RuntimeError(f"pdfinfo did not report a page count for {pdf}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--max-pages", type=int, default=1)
    ap.add_argument("--expect", nargs="*", default=[], help="strings (e.g. headings) that must appear in this order")
    ap.add_argument("--contains", nargs="*", default=[], help="strings that must survive extraction")
    ap.add_argument("--parser", choices=["poppler", "pdfminer"], default="poppler")
    ap.add_argument("--min-words", type=int, default=50, help="fail if fewer words are extracted (default 50)")
    ap.add_argument("--show", action="store_true", help="print the extracted text")
    args = ap.parse_args()

    errors = []
    pages = page_count(args.pdf)
    if pages > args.max_pages:
        errors.append(f"{pages} pages, limit is {args.max_pages}. Cut until it fits.")

    text = extract(args.pdf, args.parser)
    if args.show:
        print(text)

    words = len(text.split())
    if words < args.min_words:
        errors.append(f"only {words} words extracted (minimum {args.min_words}): blank page, image-only PDF or broken text layer")

    for ch, why in BAD_CHARS.items():
        n = text.count(ch)
        if n:
            errors.append(f"{n} x {why}")
    pua = [c for c in text if 0xE000 <= ord(c) <= 0xF8FF]
    if pua:
        errors.append(f"{len(pua)} private-use glyphs (icons or broken font mapping)")

    pos = -1
    for heading in args.expect:
        found = text.find(heading, pos + 1)
        if found < 0:
            where = "missing" if heading not in text else "out of order"
            errors.append(f"'{heading}' is {where} in the extracted text")
        else:
            pos = found

    for s in args.contains:
        if s not in text:
            errors.append(f"'{s}' not found in the extracted text")

    name = f"{args.pdf} [{args.parser}]"
    if errors:
        print(f"FAIL {name}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    order = ", reading order OK" if args.expect else ""
    print(f"PASS {name}: {pages} page(s), {words} words extracted{order}")


if __name__ == "__main__":
    main()
