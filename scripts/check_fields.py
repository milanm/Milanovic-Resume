#!/usr/bin/env python3
"""Field-level ATS check: does every fact on the resume come out of the PDF, and together?

Text alone is not enough for an applicant tracking system. It has to find the company,
the title and the dates of each job, and keep them attached to each other. This script
compares the text that three extractors pull from the PDF with a ground-truth file:

  poppler (pdftotext), pdfminer.six and PyMuPDF.

For each extractor it checks:
  - name, email, phone, location, every skill, certification and language appear verbatim;
  - for every job, the company, the title and "start – end" all appear in that job's block,
    company before title, before the next job starts (so a parser can attach them);
  - for every degree, the degree, the school and the year appear within one block.

Usage:
  python3 scripts/check_fields.py pdf/resume-latex.pdf tests/fields/resume.yml
  python3 scripts/check_fields.py pdf/junior-typst.pdf tests/fields/junior.yml --show

Needs: poppler-utils, pip install pdfminer.six pymupdf pyyaml
"""
import argparse
import re
import subprocess
import sys
import unicodedata

import yaml

DASHES = "–—‐‑−"


def norm(text):
    text = unicodedata.normalize("NFC", text)
    for d in DASHES:
        text = text.replace(d, "-")
    text = text.replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip()


def extract(pdf):
    out = {}
    out["poppler"] = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"],
                                    check=True, capture_output=True, text=True).stdout
    from pdfminer.high_level import extract_text
    out["pdfminer"] = extract_text(pdf)
    import pymupdf
    with pymupdf.open(pdf) as doc:
        out["pymupdf"] = "\n".join(page.get_text() for page in doc)
    return {k: norm(v) for k, v in out.items()}


def check(text, truth):
    errors = []

    def has(value, what):
        if norm(str(value)) not in text:
            errors.append(f"{what} not found: {value!r}")

    for key in ("name", "email", "phone", "location"):
        if truth.get(key):
            has(truth[key], key)
    for key in ("skills", "certifications", "languages"):
        for item in truth.get(key, []):
            has(item, key[:-1])

    jobs = truth.get("work", [])
    starts = [text.find(norm(j["company"])) for j in jobs]
    for i, job in enumerate(jobs):
        label = f"job {i + 1} ({job['company']})"
        start = starts[i]
        if start < 0:
            errors.append(f"{label}: company not found")
            continue
        later = [s for s in starts[i + 1:] if s > start]
        block = text[start:later[0] if later else len(text)]
        title_at = block.find(norm(job["title"]))
        if title_at < 0:
            errors.append(f"{label}: title {job['title']!r} not in the job's block")
        dates = norm(f"{job['start']} - {job['end']}")
        if dates not in block:
            errors.append(f"{label}: dates {dates!r} not in the job's block")
        if job.get("location") and norm(job["location"]) not in block:
            errors.append(f"{label}: location {job['location']!r} not in the job's block")

    for i, edu in enumerate(truth.get("education", [])):
        label = f"education {i + 1}"
        at = text.find(norm(edu["degree"]))
        if at < 0:
            errors.append(f"{label}: degree {edu['degree']!r} not found")
            continue
        block = text[at:at + len(norm(edu["degree"])) + 120]
        for key in ("school", "year"):
            if edu.get(key) and norm(str(edu[key])) not in block:
                errors.append(f"{label}: {key} {edu[key]!r} not next to the degree")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("truth")
    ap.add_argument("--show", action="store_true", help="print each extractor's normalized text")
    args = ap.parse_args()

    with open(args.truth, encoding="utf-8") as f:
        truth = yaml.safe_load(f)
    texts = extract(args.pdf)
    failed = False
    fields = 4 + sum(len(truth.get(k, [])) for k in ("skills", "certifications", "languages")) \
        + 4 * len(truth.get("work", [])) + 3 * len(truth.get("education", []))
    for name, text in texts.items():
        if args.show:
            print(f"--- {name}\n{text}\n")
        errors = check(text, truth)
        if errors:
            failed = True
            print(f"FAIL {args.pdf} [{name}]")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"PASS {args.pdf} [{name}]: {fields} fields found, jobs and degrees intact")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
