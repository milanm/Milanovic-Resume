# Contributing

Bug reports, fixes and small improvements are welcome. The template stays deliberately small: one page, one column, nothing a parser can't read.

## Before you open a pull request

1. Change the LaTeX class and the Typst library together. Both must keep producing the same page.
2. Build and check everything:

   ```bash
   make            # LuaLaTeX + Typst builds, then the text and field checks
   make edge       # long names, US Letter, 10 and 12 pt, overflow
   make verapdf    # PDF/UA validation with veraPDF (Docker)
   make visual     # page 1 of every PDF against tests/visual
   make universe   # the Typst Universe template, compiled from a local package path
   ```

   You need a current TeX Live or MiKTeX with `latexmk`, Typst 0.14 or newer, poppler-utils, Docker for `make verapdf` and `pip install pdfminer.six pymupdf pyyaml pillow`.
3. Look at the PDFs, not only at the check output. `make previews` renders `images/*.png`.
4. Keep every example on one page, keep the text layer clean and keep veraPDF passing. CI runs the same checks and fails the build otherwise.
5. If you change the design on purpose, the visual check fails. Replace `tests/visual/*.png` with the renders from the CI artifact (`build/visual/`) and say so in the pull request. If you change an example's content, update `tests/fields/`.

## What tends to get merged

- Fixes for parsing problems, with the `scripts/check_pdf.py --show` output before and after.
- Options that keep the default look unchanged.
- Documentation fixes.

## What tends not to

- Icons, photos, skill bars, sidebars or a second column for the main content.
- New dependencies for the class or the library without a strong reason.
