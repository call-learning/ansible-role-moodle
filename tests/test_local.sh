#!/bin/bash
#
# Ansible role test shim.
#
# Usage: [OPTIONS] ./tests/test.sh
#   - distro: a supported Docker distro version (default = "centos7")
#   - playbook: a playbook in the tests directory (default = "test.yml")
#   - cleanup: whether to remove the Docker container (default = true)
#   - container_id: the --name to set for the container (default = timestamp)
#   - test_idempotence: whether to test playbook's idempotence (default = true)
#
# License: MIT

# Exit on any individual command failure.
set -e

# Pretty colors.
red='\033[0;31m'
green='\033[0;32m'
neutral='\033[0m'

timestamp=$(date +%s)

# Allow environment variables to override defaults.
distro=${distro:-"ubuntu1604"}
dbengine=${dbengine:-"mysql"}
playbook=${playbook:-"test.yml"}
cleanup=${cleanup:-"true"}
container_id=${container_id:-$timestamp}
test_idempotence=${test_idempotence:-"true"}
publish_port=${publish_port:-""} # Add publish_port="-p 8000:80" to forward port 80 to 8000

## Set up vars for Docker setup.
# CentOS 7
if [ $distro = 'centos7' ]; then
  init="/usr/lib/systemd/systemd"
  opts="--privileged --volume=/sys/fs/cgroup:/sys/fs/cgroup:ro"
# Ubuntu 18.04
elif [ $distro = 'ubuntu1804' ]; then
  init="/lib/systemd/systemd"
  opts="--privileged --volume=/var/lib/docker --volume=/sys/fs/cgroup:/sys/fs/cgroup:ro"
# Ubuntu 16.04
elif [ $distro = 'ubuntu1604' ]; then
  init="/lib/systemd/systemd"
  opts="--privileged --volume=/var/lib/docker --volume=/sys/fs/cgroup:/sys/fs/cgroup:ro"
# Debian 9
elif [ $distro = 'debian9' ]; then
  init="/lib/systemd/systemd"
  opts="--privileged --volume=/sys/fs/cgroup:/sys/fs/cgroup:ro"
fi

# add the default moodle.test to the hostname for local testing
opts="$opts --add-host moodle.test:127.0.0.1 "

# Disable apparmor for mysqld as it creates issue at install (https://github.com/moby/moby/issues/7276#issuecomment-68827244)
if [[ "$distro" =~ ^ubuntu1[6-8]04 ]]  && [ -f /etc/lsb-release ] &&  [ /etc/apparmor.d/usr.sbin.mysqld ]; then
    source /etc/lsb-release
    if [ $DISTRIB_ID = 'Ubuntu' ]; then
        printf "Disabling apparmor for mysql"
        [ -f /etc/apparmor.d/disable/usr.sbin.mysqld ] || sudo ln -s /etc/apparmor.d/usr.sbin.mysqld /etc/apparmor.d/disable/
        sudo apparmor_parser -R /etc/apparmor.d/usr.sbin.mysqld || true
        sudo aa-status
    fi
fi

# Run the container using the supplied OS.
printf ${green}"Starting Docker container: geerlingguy/docker-$distro-ansible."${neutral}"\n"
docker pull geerlingguy/docker-$distro-ansible:latest
docker run $publish_port --detach --volume="$PWD":/etc/ansible/roles/role_under_test:rw --name $container_id $opts geerlingguy/docker-$distro-ansible:latest $init

printf "\n"

# Install requirements if `requirements.yml` is present.
if [ -f "$PWD/tests/requirements.yml" ]; then
  printf ${green}"Requirements file detected; installing dependencies."${neutral}"\n"
  docker exec --tty $container_id env TERM=xterm ansible-galaxy install -r /etc/ansible/roles/role_under_test/tests/requirements.yml
fi

printf "\n"

# Test Ansible syntax.
printf ${green}"Checking Ansible playbook syntax."${neutral}
docker exec --tty $container_id env TERM=xterm ansible-playbook /etc/ansible/roles/role_under_test/tests/$playbook --syntax-check

printf "\n"

# Run Ansible playbook (testing all availble tags : aurora-engine for example)
printf ${green}"Running command: docker exec $container_id env TERM=xterm ansible-playbook /etc/ansible/roles/role_under_test/tests/$playbook"${neutral}
docker exec $container_id env TERM=xterm env ANSIBLE_FORCE_COLOR=1 ansible-playbook /etc/ansible/roles/role_under_test/tests/$playbook --extra-vars "dbengine=$dbengine"

if [ "$test_idempotence" = true ]; then
  # Run Ansible playbook again (idempotence test).
  printf ${green}"Running playbook again: idempotence test"${neutral}
  idempotence=$(mktemp)
  docker exec $container_id ansible-playbook /etc/ansible/roles/role_under_test/tests/$playbook --extra-vars "dbengine=$dbengine" | tee -a $idempotence
  tail $idempotence \
    | grep -q 'changed=0.*failed=0' \
    && (printf ${green}'Idempotence test: pass'${neutral}"\n") \
    || (printf ${red}'Idempotence test: fail'${neutral}"\n" && exit 1)
fi

# Remove the Docker container (if configured).
if [ "$cleanup" = true ]; then
  printf "Removing Docker container...\n"
  docker rm -f $container_id
fi

if [[ "$distro" =~ ^ubuntu1[6-8]04 ]]  && [ -f /etc/lsb-release ] &&  [ /etc/apparmor.d/usr.sbin.mysqld ]; then
    if [ $DISTRIB_ID = 'Ubuntu' ]; then
        printf "Enabling apparmor for mysql again"
        sudo rm /etc/apparmor.d/disable/usr.sbin.mysqld || true
        sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.mysqld || true
        sudo aa-status
    fi
fi
