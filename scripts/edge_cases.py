#!/usr/bin/env python3
"""Stress-test the template: build variants of the example resume and check each one.

The examples are tuned to fit. Real resumes are not: longer names, longer links, US Letter,
other font sizes, too much experience. This script makes those variants from
latex/resume.tex and typst/resume.typ, compiles them with both engines and checks:

  letter      US Letter paper                     one page, headings in order
  font10      10 pt base size                     one page, headings in order
  font12      12 pt base size                     at most two pages, headings in order
  long        long hyphenated name, long URL      one page, name and URL extracted whole
  columns     two-column skills list              one page, every skill extracted
  overflow    experience section three times      the one-page check FAILS, and LaTeX warns

Every variant also has to keep all text inside the side margins (nothing runs off the
page) and, in LaTeX, compile without an "Overfull \\hbox" warning.

Generated sources go to latex/edge-*.tex and typst/edge-*.typ, PDFs to build/edge/.
All of them are git-ignored.

Usage:
  python3 scripts/edge_cases.py                  # both engines
  python3 scripts/edge_cases.py --engine typst   # one engine
  (CI: --write-only, compile latex/edge-*.tex with LuaLaTeX, then --latex-prebuilt)
Needs: latexmk + LuaLaTeX, Typst, poppler-utils, pip install pymupdf pdfminer.six
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "edge"
# Default for --expect; `make edge` passes RESUME_ORDER from the Makefile instead.
ORDER = ["SKILLS", "Technical strategy", "PROFESSIONAL EXPERIENCE", "EDUCATION", "CERTIFICATIONS", "LANGUAGES"]
LONG_NAME = "Dr. Maximiliana Alexandrovna Konstantinopoulou-Papadimitriou"
LONG_URL = "linkedin.com/in/maximiliana-konstantinopoulou-papadimitriou-8a4b2c19"
RIGHT_MARGIN_PT = 1.5 / 2.54 * 72   # both engines, both paper sizes
LEFT_MARGIN_PT = 1.6 / 2.54 * 72    # the smaller of the two (US Letter, LaTeX)
TOLERANCE_PT = 2.0


# ------------------------------------------------------------------ variants
# The variants are made with patterns, not exact strings, so they keep working after
# you replace my details with yours in resume.tex / resume.typ.
def experience(text, heading, next_heading):
    """Start and end of the experience section's body (or of everything after the first heading)."""
    m = re.search(heading, text)
    if not m:
        m = re.search(next_heading, text)
    a = text.index("\n", m.start()) + 1
    n = re.search(next_heading, text[a:])
    return a, a + n.start() if n else len(text)


def latex_variants(src):
    def opts(o):
        return re.sub(r"(?m)^\\documentclass(?:\[([^\]]*)\])?\{milanovic-resume\}",
                      lambda m: rf"\documentclass[{m.group(1) + ',' if m.group(1) else ''}{o}]{{milanovic-resume}}", src, count=1)
    long = re.sub(r"\\name\{[^}]*\}", lambda m: rf"\name{{{LONG_NAME}}}", src, count=1)
    long = long.replace("\\contact{%", "\\contact{%\n  \\href{https://www." + LONG_URL + "}{" + LONG_URL + "} \\sep", 1)
    a, b = experience(src, r"\\section\{Professional Experience\}", r"\\section\{|\\end\{document\}")
    return {
        "letter": opts("paper=letter"),
        "font10": opts("fontsize=10"),
        "font12": opts("fontsize=12"),
        "long": long,
        "columns": re.sub(r"\\begin\{skills\}(\[[^\]]*\])?", lambda m: r"\begin{skills}[columns]", src, count=1),
        "overflow": src[:b] + src[a:b] * 2 + src[b:],
    }


def typst_variants(src):
    def opts(key, value):
        # drop the argument if the resume already sets it: Typst refuses duplicates
        out = re.sub(rf"(?m)^[ \t]*{key}:[^\n]*\n", "", src)
        return out.replace("#show: resume.with(", f"#show: resume.with(\n  {key}: {value},", 1)
    long = re.sub(r'name: "[^"]*"', lambda m: f'name: "{LONG_NAME}"', src, count=1)
    long = long.replace("contact: (", f'contact: (\n    link("https://www.{LONG_URL}")[{LONG_URL}],', 1)
    a, b = experience(src, r"(?m)^= Professional Experience", r"(?m)^= ")
    return {
        "letter": opts("paper", '"us-letter"'),
        "font10": opts("font-size", "10pt"),
        "font12": opts("font-size", "12pt"),
        "long": long,
        "columns": src.replace("#skills(", "#skills(columns: true,", 1),
        "overflow": src[:b] + src[a:b] * 2 + src[b:],
    }


# ------------------------------------------------------------------ build
def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def build_latex(name, source, prebuilt=False):
    tex = ROOT / "latex" / f"edge-{name}.tex"
    if prebuilt:  # CI compiles latex/edge-*.tex in the TeX Live container first
        r = None
    else:
        tex.write_text(source, encoding="utf-8")
        r = run(["latexmk", "-interaction=nonstopmode", "-halt-on-error", tex.name], ROOT / "latex")
    log = tex.with_suffix(".log").read_text(encoding="utf-8", errors="replace") if tex.with_suffix(".log").exists() else ""
    pdf = tex.with_suffix(".pdf")
    if (r and r.returncode) or not pdf.exists():
        return None, log or (r.stdout + r.stderr if r else "no PDF: compile latex/edge-*.tex first")
    out = OUT / f"edge-{name}-latex.pdf"
    out.write_bytes(pdf.read_bytes())
    return out, log


def build_typst(name, source, typst):
    src = ROOT / "typst" / f"edge-{name}.typ"
    src.write_text(source, encoding="utf-8")
    out = OUT / f"edge-{name}-typst.pdf"
    r = run([typst, "compile", "--ignore-system-fonts", "--font-path", "../fonts", "--pdf-standard", "ua-1",
             src.name, str(out)], ROOT / "typst")
    if r.returncode:
        return None, r.stderr
    return out, r.stderr


# ------------------------------------------------------------------ checks
def check_pdf(pdf, *args):
    r = run([sys.executable, str(ROOT / "scripts" / "check_pdf.py"), str(pdf), *args], ROOT)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()


def margin_errors(pdf):
    import pymupdf
    errors = []
    with pymupdf.open(pdf) as doc:
        for page in doc:
            right = page.rect.width - RIGHT_MARGIN_PT + TOLERANCE_PT
            left = LEFT_MARGIN_PT - TOLERANCE_PT
            for block in page.get_text("rawdict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        # Skip spaces: tagged LuaLaTeX puts a real space after the last word
                        # of a line (so words don't merge in the text layer), past the margin.
                        boxes = [c["bbox"] for c in span["chars"] if not c["c"].isspace()]
                        if not boxes:
                            continue
                        x0, x1 = min(b[0] for b in boxes), max(b[2] for b in boxes)
                        if x1 > right or x0 < left:
                            text = "".join(c["c"] for c in span["chars"])
                            errors.append(f"page {page.number + 1}: text outside the margins "
                                          f"(x {x0:.0f}-{x1:.0f} pt): {text[:50]!r}")
    return errors


def overfull(log):
    return [l.strip() for l in log.splitlines()
            if l.startswith("Overfull \\hbox") and float(re.search(r"\(([\d.]+)pt", l).group(1)) > 0.5]


def check(name, engine, pdf, log, order):
    errors = []
    if pdf is None:
        tail = "\n    ".join([l for l in log.splitlines() if l.startswith("!") or "error" in l.lower()][:5])
        return [f"did not compile\n    {tail}"]
    if name == "overflow":
        ok, _ = check_pdf(pdf, "--max-pages", "1")
        if ok:
            errors.append("one-page check passed on a two-page resume")
        if engine == "latex" and "Your resume runs to" not in log:
            errors.append("the class did not warn about the second page")
    else:
        pages = "2" if name == "font12" else "1"
        if name == "long":
            args = ["--max-pages", pages, "--contains", "Konstantinopoulou-Papadimitriou", LONG_URL]
        elif name == "columns":
            args = ["--max-pages", pages, "--contains", *order]
        else:
            args = ["--max-pages", pages, "--expect", *order]
        ok, out = check_pdf(pdf, *args)
        if not ok:
            errors += [l for l in out if "FAIL" in l or "-" in l[:4]] or out[-3:]
        if name in ("long", "columns"):
            ok, out = check_pdf(pdf, "--max-pages", pages, "--parser", "pdfminer", *args[2:])
            if not ok:
                errors += ["pdfminer: " + l for l in out[-3:]]
    errors += margin_errors(pdf)
    if engine == "latex":
        errors += overfull(log)
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["both", "latex", "typst"], default="both")
    ap.add_argument("--typst", default="typst", help="path to the typst binary")
    ap.add_argument("--expect", nargs="+", default=ORDER,
                    help="strings that must come out in this order (default: my resume's headings)")
    ap.add_argument("--write-only", action="store_true", help="only write latex/edge-*.tex and typst/edge-*.typ")
    ap.add_argument("--latex-prebuilt", action="store_true",
                    help="check latex/edge-*.pdf and .log as they are instead of compiling them (CI)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    jobs = []
    if args.engine in ("both", "latex"):
        src = (ROOT / "latex" / "resume.tex").read_text(encoding="utf-8")
        jobs += [("latex", n, s) for n, s in latex_variants(src).items()]
    if args.engine in ("both", "typst"):
        src = (ROOT / "typst" / "resume.typ").read_text(encoding="utf-8")
        jobs += [("typst", n, s) for n, s in typst_variants(src).items()]

    if args.write_only:
        for engine, name, source in jobs:
            folder, ext = ("latex", "tex") if engine == "latex" else ("typst", "typ")
            (ROOT / folder / f"edge-{name}.{ext}").write_text(source, encoding="utf-8")
        print(f"wrote {len(jobs)} edge-case sources")
        return

    failed = 0
    for engine, name, source in jobs:
        if engine == "latex":
            pdf, log = build_latex(name, source, args.latex_prebuilt)
        else:
            pdf, log = build_typst(name, source, args.typst)
        errors = check(name, engine, pdf, log, args.expect)
        print(f"{'FAIL' if errors else 'PASS'} {engine:<5} {name}")
        for e in errors:
            print(f"    - {e}")
        failed += bool(errors)
    print(f"\n{len(jobs) - failed}/{len(jobs)} edge cases passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
