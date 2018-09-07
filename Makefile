.ONESHELL: # Force make to use a single shell for all commands in one target

mds = $(wildcard notation/*.md)  # Capture all .md files in the notation folder
texs = $(mds:notation/%.md=build/%.tex)   # Substitute filetype to tex
pdfs = $(mds:notation/%.md=output/%.pdf)  # Substitute filetype to pdf
srcs = $(wildcard *.py)

all: $(pdfs)

# Compile tex files in build/ into pdfs in output/
output/%.pdf: build/%.tex $(srcs)
	cd build/
	ls
	pdflatex $(<F)
	cd ..
	mv build/$(@F) $@

# Compile md files in notation/ to tex in build/
build/%.tex: notation/%.md $(srcs)
	./render_latex.py $< --outfile $@

.SECONDARY: $(texs)  # Prevent deletion of intermediate tex files

clean:
	rm -rf build/*
	rm -rf output/*
