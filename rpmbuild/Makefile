# -*-Makefile-*-
# Operations for building source rpms/spec files
# Creates a new rpmbuild area for each file
TOP=$(shell pwd)
TMP=/tmp
RPMS=RPMS
SRPMS=SRPMS
SOURCES=$(wildcard *.src.rpm)
SPECS=$(wildcard *.spec)

all: dst dst/a
	echo "ALL"
	touch all

dst: 
	echo INIT
	mkdir -p dst

dst/a: src/a
	echo "DST/A"
	cp src/a dst/
	
src/a:
	echo SOURCE

.PHONY: clean

clean:
	echo CLEAN
	$(RM) -r dst all



buildrpms: $(SOURCES) $(SPECS)
	echo $@ ALL $^
  
%.src.rpm: clean
	yum-builddep $*.src.rpm
	$(eval $@_TMP := $(shell mktemp -d -p $(TMP)))
	echo TEMP $($@_TMP)
	rebuild --define "_topdir $($@_TMP)" \
		--define "_builddir $($@_TMP)/BUILD" \
		--define "_buildrootdir $($@_TMP)/BUILDROOT" \
		--define "_rpmdir $(TOP)/$(RPMS)" \
		--define "_srcrpmdir $(TOP)/$(SRPMS)" \
		--rebuild -ba $*.src.rpm
	$(RM) -r $($@_TMP)
	cp $*.src.rpm $(TOP)/$(SRPMS)/
  
%.spec: clean
	yum-builddep $*.spec
	$(eval $@_TMP := $(shell mktemp -d -p $(TMP)))
	echo TEMP $($@_TMP)
	rebuild --define "_topdir $($@_TMP)" \
		--define "_builddir $($@_TMP)/BUILD" \
		--define "_buildrootdir $($@_TMP)/BUILDROOT" \
		--define "_rpmdir $(TOP)/$(RPMS)" \
		--define "_srcrpmdir $(TOP)/$(SRPMS)" \
		-ba $*.src.rpm
	$(RM) -r $($@_TMP)
  
$(SRPMS)/%.src.rpm: $(SOURCES) $(SPECS)

build: $(SOURCES) $(SPECS)
	createrepo $(TOP)/$(RPMS)


cleanrpms:
	-$(RM) -r $(RPMS) $(SRPMS)
  
  
  
