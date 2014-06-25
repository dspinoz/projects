# -*-Makefile-*-
# Operations for building source rpms/spec files
# Creates a new rpmbuild area for each file
TOP=$(shell pwd)
TMP=/tmp
RPMS=RPMS
SRPMS=SRPMS
SOURCES=$(wildcard *.src.rpm)

.PHONY: clean all

all: $(RPMS) $(SRPMS) $(addprefix $(SRPMS), $(SOURCES))

$(RPMS): 
	mkdir -p $(RPMS)
  
$(SRPMS): 
	mkdir -p $(SRPMS)
  
$(SRPMS)/%.src.rpm: %.src.rpm
	@echo Installing dependencies $<
	sudo yum-builddep $<
	$(eval $@_TMP := $(shell mktemp -d -p $(TMP)))
	rebuild --define "_topdir $($@_TMP)" \
		--define "_builddir $($@_TMP)/BUILD" \
		--define "_buildrootdir $($@_TMP)/BUILDROOT" \
		--define "_rpmdir $(TOP)/$(RPMS)" \
		--define "_srcrpmdir $(TOP)/$(SRPMS)" \
		--rebuild -ba $<
	$(RM) -r $($@_TMP)
	cp $< $(TOP)/$(SRPMS)/
	@echo Successfully built package $@
  

clean:
	-$(RM) -r $(RPMS) $(SRPMS)
  
  
  
