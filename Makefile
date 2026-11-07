# Build every PDF, run the ATS check, render the README previews.
# Needs: XeLaTeX + latexmk (TeX Live or MiKTeX), Typst 0.14+, poppler-utils, Python 3 with pdfminer.six.

TYPST    ?= typst
SECTIONS := SKILLS "PROFESSIONAL EXPERIENCE" EDUCATION CERTIFICATIONS LANGUAGES
DOCS     := resume template cover-letter
PKG_VER  := $(shell sed -n 's/^version = "\(.*\)"/\1/p' typst/typst.toml)

.PHONY: all latex typst check previews overleaf universe clean

all: latex typst check

latex:
	@mkdir -p pdf
	cd latex && for f in $(DOCS); do latexmk -silent $$f.tex && cp $$f.pdf ../pdf/$$f-latex.pdf; done

typst:
	@mkdir -p pdf
	cd typst && for f in $(DOCS); do $(TYPST) compile --ignore-system-fonts --font-path ../fonts $$f.typ ../pdf/$$f-typst.pdf; done

check:
	for e in latex typst; do \
	  python3 scripts/check_pdf.py pdf/resume-$$e.pdf --expect $(SECTIONS) --contains "Milanović" "milan@example.com" "cloud-native" && \
	  python3 scripts/check_pdf.py pdf/template-$$e.pdf --expect SKILLS "PROFESSIONAL EXPERIENCE" "SELECTED PROJECTS" EDUCATION && \
	  python3 scripts/check_pdf.py pdf/cover-letter-$$e.pdf --contains "Dear Ms. Kim" || exit 1; \
	done
	# Stricter parser on the Typst output (see README: XeLaTeX limitation)
	python3 scripts/check_pdf.py pdf/resume-typst.pdf --parser pdfminer --expect $(SECTIONS) --contains "Milanović" "cloud-native"
	python3 scripts/check_pdf.py pdf/template-typst.pdf --parser pdfminer
	python3 scripts/check_pdf.py pdf/cover-letter-typst.pdf --parser pdfminer

previews:
	@mkdir -p images
	pdftoppm -r 110 -png -singlefile pdf/resume-latex.pdf images/resume
	pdftoppm -r 110 -png -singlefile pdf/template-latex.pdf images/template
	pdftoppm -r 110 -png -singlefile pdf/cover-letter-latex.pdf images/cover-letter

# Typst Universe: install the package into a local package path and compile the
# template exactly as `typst init @preview/milanovic-resume` would create it.
universe:
	rm -rf build/pkg build/init
	mkdir -p build/pkg/preview/milanovic-resume/$(PKG_VER) build/init
	cp -r typst/lib.typ typst/typst.toml typst/README.md typst/LICENSE typst/template build/pkg/preview/milanovic-resume/$(PKG_VER)/
	cp typst/template/main.typ build/init/
	$(TYPST) compile --package-path build/pkg --ignore-system-fonts --font-path fonts build/init/main.typ build/init/main.pdf
	python3 scripts/check_pdf.py build/init/main.pdf --expect SKILLS "PROFESSIONAL EXPERIENCE" "SELECTED PROJECTS" EDUCATION

# Zip for "Open in Overleaf": LaTeX files and fonts in one flat folder.
overleaf:
	rm -rf build/overleaf && mkdir -p build/overleaf/fonts
	cp latex/milanovic-resume.cls latex/*.tex latex/latexmkrc build/overleaf/
	cp fonts/*.otf fonts/OFL.md build/overleaf/fonts/
	cd build/overleaf && zip -qr ../Milanovic-Resume-overleaf.zip .

clean:
	cd latex && latexmk -C -silent $(addsuffix .tex,$(DOCS))
	rm -rf build
