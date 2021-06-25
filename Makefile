STATIC=/usr/share
PROJECT=builder-ci

all: build

build:
	echo "Nothing to build"

install:
	
	## Copy static files
	mkdir -p $(DESTDIR)$(STATIC)/$(PROJECT)/
	cp -R listener.py app.py wsgi.py lib $(DESTDIR)$(STATIC)/$(PROJECT)/

	## Copy executable
	mkdir $(DESTDIR)/usr/bin/
	cp cli.py $(DESTDIR)/usr/bin/builder-ci
	sed -i "s|sys.path.append.*|sys.path.append(\'$(STATIC)/$(PROJECT)/lib\')|"  $(DESTDIR)/usr/bin/builder-ci
	sed -i "s|sys.path.append.*|sys.path.append(\'$(STATIC)/$(PROJECT)/lib\')|"  $(DESTDIR)$(STATIC)/$(PROJECT)/listener.py
	sed -i "s|config.read.*|config.read(\'/etc/builder-ci/builder-ci.conf\')|" $(DESTDIR)$(STATIC)/$(PROJECT)/lib/config.py
	
	## Copy config template
	mkdir -p $(DESTDIR)/etc/$(PROJECT)
	cp config.ini $(DESTDIR)/etc/$(PROJECT)/$(PROJECT).conf

	## Copy helpers and docker builds
	mkdir -p $(DESTDIR)$(STATIC)/doc/$(PROJECT)/
	cp -a docker helpers $(DESTDIR)$(STATIC)/doc/$(PROJECT)/

	## Generate documentation
	python3 gen_doc.py > api-call.json

clean:
	echo "Nothing to clean"
