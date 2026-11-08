#!/usr/bin/env python3
"""Send a resume PDF to commercial resume parsers and score what they get back.

check_fields.py proves the facts are in the PDF's text layer. This script asks the next
question: do real parsers, the kind applicant tracking systems license, put those facts in
the right fields? It sends the PDF to several parsers through Eden AI's resume_parser
endpoint and compares each parser's structured output with the same ground-truth file
check_fields.py uses (tests/fields/*.yml).

Scored fields: name, email, phone, location; for every job the company, title, start year
and end year; for every degree the school and the degree. Matching ignores case, accents
and punctuation, so "Milanovic" counts for "Milanović". A field counts as found only when
the parser returns it in the right slot: a job title under the right company, not just
somewhere in the response.

Idea and endpoint taken from RenderCV's ATS tests (MIT): https://github.com/rendercv/rendercv

Usage:
  export EDENAI_API_KEY=...          # never commit it; the script only reads the env var
  python3 scripts/ats_parsers.py pdf/resume-latex.pdf tests/fields/resume.yml \\
          --save tests/ats/resume-latex.json
  python3 scripts/ats_parsers.py tests/ats/resume-latex.json tests/fields/resume.yml   # re-score, no API call
  python3 scripts/ats_parsers.py tests/ats/*.json --truth-dir tests/fields --table      # README table

Each call costs Eden AI credits (about $0.07-0.10 per parser per file), so this is not in CI.
Needs: pip install requests pyyaml
"""
import argparse
import difflib
import json
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from check_fields import load_truth  # same ground-truth loader as the field check

ENDPOINT = "https://api.edenai.run/v2/ocr/resume_parser"
DEFAULT_PROVIDERS = "affinda,extracta,klippa"
HONORIFICS = {"dr", "mr", "mrs", "ms", "prof", "phd"}


# ------------------------------------------------------------------ matching
def key(text):
    """Lowercase, strip accents and punctuation, collapse spaces."""
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(c for c in text if not unicodedata.combining(c)).casefold()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similar(found, want, ratio=0.85):
    a, b = key(found), key(want)
    if not a or not b:
        return False
    short, long_ = sorted((a, b), key=len)
    # containment counts only when little is missing: "3MD Inc." for "3MD Inc" yes,
    # a degree cut off after "M.Sc. in" no
    if short in long_ and len(short) >= 0.6 * len(long_):
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= ratio


def name_key(text):
    return " ".join(w for w in key(text).split() if w not in HONORIFICS)


def digits(text):
    return re.sub(r"\D", "", str(text or ""))


def year(text):
    m = re.search(r"(19|20)\d\d", str(text or ""))
    return m.group(0) if m else ""


def is_present(text):
    return not text or "present" in key(text) or "current" in key(text) or "now" == key(text)


def location_text(loc):
    if isinstance(loc, dict):
        parts = [loc.get(k) for k in ("formatted_location", "raw_input_location", "city", "region", "country")]
        return " ".join(p for p in parts if p)
    return str(loc or "")


# ------------------------------------------------------------------ scoring
def score(data, truth, run_year):
    """Return a list of (field, wanted, found, ok) rows for one parser's extracted_data."""
    rows = []
    info = data.get("personal_infos") or {}

    if truth.get("name"):
        name = info.get("name") or {}
        found = name.get("raw_name") or " ".join(x for x in (name.get("first_name"), name.get("last_name")) if x)
        rows.append(("name", truth["name"], found, name_key(found) == name_key(truth["name"])
                     or similar(name_key(found), name_key(truth["name"]), 0.9)))
    if truth.get("email"):
        mails = info.get("mails") or []
        rows.append(("email", truth["email"], ", ".join(mails),
                     any(m.strip().lower() == truth["email"].lower() for m in mails)))
    if truth.get("phone"):
        phones = info.get("phones") or []
        rows.append(("phone", truth["phone"], ", ".join(phones),
                     any(digits(p).endswith(digits(truth["phone"])[-8:]) for p in phones)))
    if truth.get("location"):
        found = location_text(info.get("address"))
        city = truth["location"].split(",")[0]
        rows.append(("location", truth["location"], found, bool(found) and key(city) in key(found)))

    entries = (data.get("work_experience") or {}).get("entries") or []
    for i, job in enumerate(truth.get("work", []), 1):
        hit = next((e for e in entries if similar(e.get("company"), job["company"])), None)
        label = f"job {i}"
        rows.append((f"{label} company", job["company"], hit.get("company") if hit else "", hit is not None))
        if not hit:
            for what, want in (("title", job["title"]), ("start", job["start"]), ("end", job["end"])):
                rows.append((f"{label} {what}", want, "(company not found)", False))
            continue
        rows.append((f"{label} title", job["title"], hit.get("title") or "", similar(hit.get("title"), job["title"])))
        rows.append((f"{label} start", job["start"], hit.get("start_date") or "", year(hit.get("start_date")) == year(job["start"])))
        end = hit.get("end_date")
        if is_present(job["end"]):  # some parsers turn "Present" into the date they parsed the file
            ok = is_present(end) or year(end) >= str(run_year - 1)
        else:
            ok = year(end) == year(job["end"])
        rows.append((f"{label} end", job["end"], end or "(empty = present)", ok))

    # Parsers disagree on where the degree goes: some fill "title", others put a level
    # there ("Master") and the degree itself in "accreditation". Either slot counts.
    entries = (data.get("education") or {}).get("entries") or []

    def degree_of(e, want):
        for slot in ("title", "accreditation"):
            if similar(e.get(slot), want, 0.75):
                return e.get(slot)
        return None

    def years_of(e):
        return {year(e.get("start_date")), year(e.get("end_date"))} - {""}

    used = set()
    for i, edu in enumerate(truth.get("education", []), 1):
        label = f"degree {i}"
        # schools repeat (two degrees from one university), so match on the degree first
        free = [n for n in range(len(entries)) if n not in used]
        pick = next((n for n in free if degree_of(entries[n], edu["degree"])), None)
        if pick is None:
            pick = next((n for n in free if similar(entries[n].get("establishment"), edu["school"])
                         and year(edu["year"]) in years_of(entries[n])), None)
        hit = entries[pick] if pick is not None else {}
        if pick is not None:
            used.add(pick)
        got = degree_of(hit, edu["degree"]) if hit else None
        shown = got or " / ".join(str(hit.get(k)) for k in ("title", "accreditation") if hit.get(k))
        rows.append((f"{label} degree", edu["degree"], shown, got is not None))
        rows.append((f"{label} school", edu["school"], hit.get("establishment") or "",
                     similar(hit.get("establishment"), edu["school"])))
    return rows


# ------------------------------------------------------------------ I/O
def call_eden(pdf, providers):
    import requests

    api_key = os.environ.get("EDENAI_API_KEY")
    if not api_key:
        sys.exit("Set EDENAI_API_KEY (an Eden AI API key) in the environment.")
    with open(pdf, "rb") as f:
        r = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {api_key}"},
                          files={"file": (Path(pdf).name, f, "application/pdf")},
                          data={"providers": providers, "response_as_dict": "true",
                                "show_original_response": "false"},
                          timeout=300)
    if r.status_code != 200:
        sys.exit(f"Eden AI returned HTTP {r.status_code}: {r.text[:300]}")
    return r.json()


def report(source, raw, truth, show_all):
    # Score "Present" against the day the parsers ran, not today, so saved results stay reproducible.
    run_year = int(str(raw.get("_run_date", date.today().isoformat()))[:4])
    results = {}
    for provider, body in sorted(raw.items()):
        if not isinstance(body, dict):
            continue
        if body.get("status") != "success":
            err = body.get("error") or {}
            print(f"\n{provider}: failed ({err.get('message', err) if isinstance(err, dict) else err})")
            results[provider] = None
            continue
        rows = score(body.get("extracted_data") or {}, truth, run_year)
        ok = sum(r[3] for r in rows)
        results[provider] = (ok, len(rows))
        print(f"\n{provider}: {ok}/{len(rows)} fields in the right slot  [{source}]")
        for field, want, found, good in rows:
            if show_all or not good:
                mark = "ok  " if good else "MISS"
                print(f"  {mark} {field:<16} want {str(want)!r:<44} got {str(found)!r}")
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="a PDF and its truth .yml, or saved .json results")
    ap.add_argument("--providers", default=DEFAULT_PROVIDERS)
    ap.add_argument("--save", help="write the raw Eden AI response here (PDF mode)")
    ap.add_argument("--truth-dir", help="find each saved result's truth file here: resume-latex.json -> resume.yml")
    ap.add_argument("--all", action="store_true", help="print matched fields too, not only misses")
    ap.add_argument("--table", action="store_true", help="print a Markdown table of scores at the end")
    args = ap.parse_args()

    jobs = []  # (label, raw, truth)
    if args.inputs[0].endswith(".pdf"):
        if len(args.inputs) != 2:
            ap.error("PDF mode takes exactly: PDF TRUTH.yml")
        pdf, truth_file = args.inputs
        raw = call_eden(pdf, args.providers)
        raw["_run_date"] = date.today().isoformat()
        if args.save:
            Path(args.save).parent.mkdir(parents=True, exist_ok=True)
            Path(args.save).write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        jobs.append((Path(pdf).stem, raw, truth_file))
    else:
        files = args.inputs
        if not args.truth_dir:
            *files, truth_file = files
        for f in files:
            if args.truth_dir:
                truth_file = str(Path(args.truth_dir) / (Path(f).stem.rsplit("-", 1)[0] + ".yml"))
            jobs.append((Path(f).stem, json.loads(Path(f).read_text(encoding="utf-8")), truth_file))

    table = []
    for label, raw, truth_file in jobs:
        truth = load_truth(truth_file)
        for provider, res in report(label, raw, truth, args.all).items():
            table.append((label, provider, res))

    if args.table:
        # leave out a provider that failed on every file (down that day, not a score)
        providers = sorted({p for _, p, r in table if r is not None})
        labels = list(dict.fromkeys(l for l, _, _ in table))
        cells = {(l, p): r for l, p, r in table}
        print("\n| PDF | " + " | ".join(p.capitalize() for p in providers) + " |")
        print("|---|" + "---|" * len(providers))
        for l in labels:
            row = []
            for p in providers:
                r = cells.get((l, p))
                row.append("failed" if r is None else f"{r[0]}/{r[1]}")
            print(f"| `{l}.pdf` | " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
