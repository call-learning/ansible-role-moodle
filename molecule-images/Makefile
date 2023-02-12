# Makefile to build all given image

# Two ways to use this makefile:
# 1- make <build image target> : make rockylinux9 - will build rockylinux image
# 2- make, will build all images

.DEFAULT_GOAL := builds

DBFLAVORS=mysql postgres
ALL_TARGETS=rockylinux9 debian12 ubuntu2204

.PHONY: builds $(ALL_TARGETS)

builds: $(ALL_TARGETS)

$(ALL_TARGETS):
	for DBFLAVOR in $(DBFLAVORS); \
	do \
		packer build -var-file=./vars/$@.vars.json -var="docker_image_dbflavor=$$DBFLAVOR" moodle-ami.json ; \
	done

push:
	for IMAGE in `docker image ls calllearning/*-moodle-ansible --format "{{.Repository}}:{{.Tag}}"`; \
	do \
		docker push $$IMAGE; \
	done

clean:
	for IMAGE in `docker image ls calllearning/*-moodle-ansible --format "{{.ID}}"`; \
	do \
		docker image rm $$IMAGE; \
	done
