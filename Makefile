.ONESHELL: # Force make to use a single shell for all commands in one target

mds = $(wildcard notation/*.md)
texs = $(mds:notation/%.md=build/%.tex)
pdfs = $(mds:notation/%.md=output/%.pdf)

all: $(pdfs)

output/%.pdf: build/%.tex
	cd build/
	ls
	pdflatex $(<F)
	cd ..
	mv build/$(@F) $@

build/%.tex: notation/%.md
	./render_latex.py $< --outfile $@

.SECONDARY: $(texs)  # Prevent deletion of intermediate tex files

clean:
	rm -rf build/*
	rm -rf output/*
