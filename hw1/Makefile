# You may override this variable from the command line. E.g.:
# make target=foo
# make clean target=foo
main = main

.PHONY : clean all

all : clean main

clean :
	for i in aux log bbl blg bcf out run.xml pdf fls fdb_latexmk vrb snm nav toc; do \
		rm -f *.$$i; \
	done
	-rm -f *~

# You may append other dependencies
main : $(main).tex
	$(eval basename = $(patsubst %.tex,%,$<))
	xelatex $(basename)
