# Makefile for gif2png

VERSION = $(shell sed -n <NEWS '/::/s/^\([^:]*\).*/\1/p' | head -1)

TAR = tar

all: gif2png gif2png.1 web2png.1

GOFLAGS=-gcflags '-N -l'
gif2png: gif2png.go
	go build $(GOFLAGS) -o gif2png gif2png.go

gif2png.1: gif2png.xml
	xmlto man gif2png.xml

gif2png.html: gif2png.xml
	xmlto html-nochunks gif2png.xml

web2png.1: web2png.xml
	xmlto man web2png.xml

check:
	cd test; make --quiet test

clean:
	rm -f gif2png gif2png.1 web2png.1 index.html

version:
	@echo $(VERSION)

prefix ?= /usr
bindir ?= $(prefix)/bin
mandir ?= $(prefix)/share/man

install: gif2png gif2png.1 web2png.1
	mkdir -p $(DESTDIR)$(bindir)
	mkdir -p $(DESTDIR)$(mandir)/man1
	cp gif2png web2png $(DESTDIR)$(bindir)/
	cp gif2png.1 web2png.1 $(DESTDIR)$(mandir)/man1/

uninstall:
	rm $(bindir)/gif2png $(bindir)/web2png
	rm $(mandir)/man1/gif2png.1 $(mandir)/man1/web2png.1

PYLINTOPTS = --rcfile=/dev/null --reports=n
pylint:
	@pylint $(PYLINTOPTS) web2png

EXTRA_DIST = README NEWS INSTALL control Makefile web2png \
	gif2png.xml web2png.xml gif2png.1 web2png.1 gif2png-logo.xcf gif2png-logo.png test
DISTFILES = gif2png.go $(EXTRA_DIST)

gif2png-$(VERSION).tar.gz: $(DISTFILES)
	$(TAR) --transform='s:^:gif2png-$(VERSION)/:' --show-transformed-names -czf gif2png-$(VERSION).tar.gz $(DISTFILES)

dist: gif2png-$(VERSION).tar.gz

release: gif2png-$(VERSION).tar.gz gif2png.html
	shipper version=$(VERSION) | sh -e -x

refresh: gif2png.html
	shipper -N -w version=$(VERSION) | sh -e -x
