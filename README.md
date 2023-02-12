# Ansible Role: Moodle

[![CI](https://github.com/call-learning/ansible-role-moodle/actions/workflows/ci.yml/badge.svg)](https://github.com/call-learning/ansible-role-moodle/actions/workflows/ci.yml)

Installs Moodle (4.1+) on RedHat and Debian/Ubuntu servers.
Tested with Ansible 5.0

## Requirements

Needs to be a recent LTS release of Ubuntu or REL which have PHP 8.0+, Apache 2.4 and 
Postgres or Mysql installed.
 

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

## Dependencies

No dependencies if the host is installed and setup with a LAMP stack 
( or similar ) environement.
If you are required to install the full environment, I suggest you check:
 - geerlingguy.php (Install of PHP 8.x or earlier)
 - geerlingguy.apache (Installation of Apache 2.x)
 - geerlingguy.postgresql (Installation of Postgres)
 - geerlingguy.mysql (Installatiion of Mysql)

## Example Playbook

## License

MIT / BSD

## Author Information

This role was created in 2017 by [Laurent David](https://github.com/laurentdavid), from 
[Jeff Geerling](https://www.jeffgeerling.com/) roles templates author of 
[Ansible for DevOps](https://www.ansiblefordevops.com/).

## Testing

### Prerequisites

You muse have the following installed:
 - ansible 

We have used Jeff Geerling's tests as a base which is in turn using 
extensively [molecule](https://ansible.readthedocs.io/projects/molecule/).
We are now using github action to run the tests at each commit (you can find them in the .github/workflow folder):
- lint.yml will just lint all project and check for any syntax error
- molecule.yml will run each scenario in turn and check if the ansible playbook is valid

Note: as installing Postgres and Mysql takes a while from the original [Jeff Geerling image](https://github.com/geerlingguy/docker-ubuntu2004-ansible)
we have a process of prebuilding those images using [packer](https://www.packer.io/) each month. This
process is done in the foler molecule-images that can be safely ignored if you are just looking for information about 
the role itself.
 
- Once the docker has been launch you can rerun the playbook by running:
```bash
    container_id=xxxxyyy
    docker exec --tty $container_id env TERM=xterm ansible-playbook /etc/ansible/roles/role_under_test/tests/test.yml
```

To test specific playbook such as the check_moodle.py part:
 
```bash
    container_id=xxxxyyy
    docker exec $container_id env TERM=xterm env ANSIBLE_FORCE_COLOR=1 ansible-playbook -i 'localhost,' -M /etc/ansible/roles/role_under_test/library /etc/ansible/roles/role_under_test/tests/test-check-moodle.yml
```

### Library testing
There is a small module that checks if moodle is installed/configured in the library folder.
More info in the README.md of the library folder.

## #TODO

- Tags tasks 
    -  Pure setup without running moodle install (just folders and source code)
    -  Install with moodle install,
    - ...  some optional task such as change password, update, dump database, ...
      
