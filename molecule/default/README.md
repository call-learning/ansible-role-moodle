# Ansible Role tests 

This now uses Molecule. You need to install it and all dependencies to be able to 
run the tests. We will use goss for the tests

```bash
    pip uninstall -y docker docker-py
    pip install docker docker-compose molecule==2.22 molecule-goss
```


To launch the test do:

```bash
    molecule check
```


## Checking the container

```bash
    container_id=xxxxyyy
    docker exec -it --tty $container_id env TERM=xterm bash
```


## Possible issues

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

