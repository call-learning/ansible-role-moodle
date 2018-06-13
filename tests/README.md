# Ansible Role tests

Instruction and test scripts created originally by Jeff Geerling (https://github.com/geerlingguy)

To run the test playbook(s) in this directory:

  1. Install and start Docker.
  1. You can either use the test.sh already in this folder. Optionally you can download/update this script 
  Jeff Geerling's created) into `tests/test.sh`:
     - `wget -O tests/test.sh https://gist.githubusercontent.com/geerlingguy/73ef1e5ee45d8694570f334be385e181/raw/`
     - Make the test shim executable: `chmod +x tests/test.sh`.
  1. Run (from the role root directory) `distro=[distro] playbook=[playbook] ./tests/test.sh`
  1. To change database engine from postgres to mysql do `dbengine=mysql ./tests/test.sh`
  1. To login on an existing container: 
```bash
    container_id=xxxxyyy
    docker exec -it --tty $container_id env TERM=xterm bash
```


If you don't want the container to be automatically deleted after the test playbook is run, add the following environment variables: `cleanup=false container_id=$(date +%s)`

## Known issues

### Local testing and apparmor on ubuntu

I stumbled on an issue with apparmor and mysql that prevents mysql from accessing /etc/mysql/conf.d 
("mysqld: Can't read dir of '/etc/mysql/conf.d/' (Errcode: 13 - Permission denied)").

It seems that it is a recuring issue with apparmor and docker on priviledged instances (--priviledged).
Seems that it works on the travis-ci environment without an issue but the local test systematically
fails at this stage.
It seems from the logs that apparmors tries to read a file on the /var/lib/overlay2 (overlay filesystem)
that is not mounted on the guest OS.

I posted an issue on the main mysql role here: https://github.com/geerlingguy/ansible-role-mysql/issues/263

Looking at similar issue from other users 

Some more info: 

  - https://github.com/moby/moby/issues/5490
  - https://blogs.oracle.com/jsmyth/apparmor-and-mysql
  - https://github.com/moby/moby/issues/7512#issuecomment-51845976

