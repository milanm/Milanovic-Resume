# Build every PDF, run the ATS check, render the README previews.
# Needs: XeLaTeX + latexmk (TeX Live or MiKTeX), Typst 0.14+, poppler-utils, Python 3 with pdfminer.six.

TYPST    ?= typst
SECTIONS := SKILLS "PROFESSIONAL EXPERIENCE" EDUCATION CERTIFICATIONS LANGUAGES
DOCS     := resume template cover-letter

.PHONY: all latex typst check previews overleaf clean

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

# Zip for "Open in Overleaf": LaTeX files and fonts in one flat folder.
overleaf:
	rm -rf build/overleaf && mkdir -p build/overleaf/fonts
	cp latex/milanovic-resume.cls latex/*.tex latex/latexmkrc build/overleaf/
	cp fonts/*.otf fonts/OFL.md build/overleaf/fonts/
	cd build/overleaf && zip -qr ../Milanovic-Resume-overleaf.zip .

clean:
	cd latex && latexmk -C -silent $(addsuffix .tex,$(DOCS))
	rm -rf build
