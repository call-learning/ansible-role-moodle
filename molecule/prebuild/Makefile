# Makefile to build the given image

setup: ansible-roles.yml
	ansible-galaxy install --force -r ansible-roles.yml -p roles/

build-common:
	packer build -var='docker_image_type=centos' -var='docker_image_version=8' -var='docker_image_dbflavor='$DBFLAVOR'' moodle-ami.json
	packer build -var='docker_image_type=ubuntu' -var='docker_image_version=1804' -var='docker_image_dbflavor='$DBFLAVOR''  moodle-ami.json
	packer build -var='docker_image_type=debian' -var='docker_image_version=10'  -var='docker_image_dbflavor='$DBFLAVOR''  moodle-ami.json

build-mysql: DBFLAVOR="mysql"
build-mysql: build-common

build-postgres: DBFLAVOR="postgres"
build-postgres: build-common

build: build-postgres build-mysql
