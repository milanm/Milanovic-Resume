# Contributing

Bug reports, fixes and small improvements are welcome. The template stays deliberately small: one page, one column, nothing a parser can't read.

## Before you open a pull request

1. Change the LaTeX class and the Typst library together. Both must keep producing the same page.
2. Build and check everything:

   ```bash
   make            # LuaLaTeX + Typst builds, then the ATS check
   make universe   # the Typst Universe template, compiled from a local package path
   ```

   You need a current TeX Live or MiKTeX with `latexmk`, Typst 0.14 or newer, poppler-utils and `pip install pdfminer.six`.
3. Look at the PDFs, not only at the check output. `make previews` renders `images/*.png`.
4. Keep every example on one page and keep the text layer clean. CI runs the same checks and fails the build otherwise.

## What tends to get merged

- Fixes for parsing problems, with the `scripts/check_pdf.py --show` output before and after.
- Options that keep the default look unchanged.
- Documentation fixes.

## What tends not to

- Icons, photos, skill bars, sidebars or a second column for the main content.
- New dependencies for the class or the library without a strong reason.
