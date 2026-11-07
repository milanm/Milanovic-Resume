# Build every PDF, run the ATS check, render the README previews.
# Needs: LuaLaTeX + latexmk from a current TeX Live or MiKTeX (CI uses the latest TeX Live), Typst 0.14+, poppler-utils, Python 3 with pdfminer.six.

TYPST    ?= typst
DOCS     := resume template cover-letter junior
PKG_VER  := $(shell sed -n 's/^version = "\(.*\)"/\1/p' typst/typst.toml)

# ---- What the ATS check expects to find. CHANGE THESE when you put in your own details.
# Strings listed in an *_ORDER variable must appear in exactly that order in the extracted text.
RESUME_ORDER   := "Milanović" SKILLS "Technical strategy" "PROFESSIONAL EXPERIENCE" EDUCATION CERTIFICATIONS LANGUAGES
RESUME_HAS     := "milan@example.com" "cloud-native"
TEMPLATE_ORDER := "Your Name" SKILLS "Language 1" "PROFESSIONAL EXPERIENCE" "SELECTED PROJECTS" EDUCATION
LETTER_ORDER   := "Milanović" "Dear Ms. Kim" "Sincerely"
JUNIOR_ORDER   := "Ana Petrović" SKILLS "C\#" "PROFESSIONAL EXPERIENCE" "SELECTED PROJECTS" EDUCATION
# One page by default. Raise it if you decide your experience needs two.
MAX_PAGES      := 1

.PHONY: all latex typst check previews overleaf universe clean

all: latex typst check

# Old PDFs are deleted first and the loop stops at the first failure, so a broken
# build can never leave a stale PDF behind for the check to pass on.
latex:
	@mkdir -p pdf
	rm -f $(foreach f,$(DOCS),pdf/$(f)-latex.pdf)
	cd latex && for f in $(DOCS); do latexmk -silent $$f.tex && cp $$f.pdf ../pdf/$$f-latex.pdf || exit 1; done

typst:
	@mkdir -p pdf
	rm -f $(foreach f,$(DOCS),pdf/$(f)-typst.pdf)
	cd typst && for f in $(DOCS); do $(TYPST) compile --ignore-system-fonts --font-path ../fonts $$f.typ ../pdf/$$f-typst.pdf || exit 1; done

check:
	for e in latex typst; do \
	  python3 scripts/check_pdf.py pdf/resume-$$e.pdf --max-pages $(MAX_PAGES) --expect $(RESUME_ORDER) --contains $(RESUME_HAS) && \
	  python3 scripts/check_pdf.py pdf/template-$$e.pdf --max-pages $(MAX_PAGES) --expect $(TEMPLATE_ORDER) && \
	  python3 scripts/check_pdf.py pdf/cover-letter-$$e.pdf --expect $(LETTER_ORDER) && \
	  python3 scripts/check_pdf.py pdf/junior-$$e.pdf --max-pages $(MAX_PAGES) --expect $(JUNIOR_ORDER) || exit 1; \
	done
	# pdfminer.six: a parser that ignores ActualText hints. Its layout heuristic
	# reorders centred headings, so it checks content, not order.
	for e in latex typst; do \
	  python3 scripts/check_pdf.py pdf/resume-$$e.pdf --max-pages $(MAX_PAGES) --parser pdfminer --contains $(RESUME_ORDER) $(RESUME_HAS) && \
	  python3 scripts/check_pdf.py pdf/template-$$e.pdf --max-pages $(MAX_PAGES) --parser pdfminer --contains $(TEMPLATE_ORDER) && \
	  python3 scripts/check_pdf.py pdf/cover-letter-$$e.pdf --parser pdfminer --contains $(LETTER_ORDER) && \
	  python3 scripts/check_pdf.py pdf/junior-$$e.pdf --max-pages $(MAX_PAGES) --parser pdfminer --contains $(JUNIOR_ORDER) || exit 1; \
	done

previews:
	@mkdir -p images
	pdftoppm -r 110 -png -singlefile pdf/resume-latex.pdf images/resume
	pdftoppm -r 110 -png -singlefile pdf/template-latex.pdf images/template
	pdftoppm -r 110 -png -singlefile pdf/cover-letter-latex.pdf images/cover-letter
	pdftoppm -r 110 -png -singlefile pdf/junior-latex.pdf images/junior

# Typst Universe: install the package into a local package path and compile the
# template exactly as `typst init @preview/milanovic-resume` would create it.
universe:
	rm -rf build/pkg build/init
	mkdir -p build/pkg/preview/milanovic-resume/$(PKG_VER) build/init
	cp -r typst/lib.typ typst/typst.toml typst/README.md typst/LICENSE typst/template build/pkg/preview/milanovic-resume/$(PKG_VER)/
	cp typst/template/main.typ build/init/
	$(TYPST) compile --package-path build/pkg --ignore-system-fonts --font-path fonts build/init/main.typ build/init/main.pdf
	python3 scripts/check_pdf.py build/init/main.pdf --expect $(TEMPLATE_ORDER)
	python3 scripts/check_pdf.py build/init/main.pdf --parser pdfminer --contains $(TEMPLATE_ORDER)

# Zip for "Open in Overleaf": LaTeX files and fonts in one flat folder.
overleaf:
	rm -rf build/overleaf && mkdir -p build/overleaf/fonts
	cp latex/milanovic-resume.cls latex/*.tex latex/latexmkrc build/overleaf/
	cp fonts/*.otf fonts/OFL.md build/overleaf/fonts/
	cd build/overleaf && zip -qr ../Milanovic-Resume-overleaf.zip .

clean:
	cd latex && latexmk -C -silent $(addsuffix .tex,$(DOCS))
	rm -rf build
