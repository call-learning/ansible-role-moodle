# Ansible Role tests 

This now uses Molecule. You need to install it and all dependencies to be able to 
run the tests. 
Images are now based upon prebuilt PHP/MySQL images so to speed up the test process.

We use molecule 3.x version.

```bash
    pip uninstall -y docker docker-py
    pip install molecule ansible-lint docker flake8 yamllint
```


To launch the test do:

```bash
    molecule test
```


## Checking the container


```bash
    molecule converge
    molecule login
```

## Distro-specific Molecule tasks

Common scenario playbooks include optional distro-specific task files from
`distro-specifics`.

Files are named from Ansible facts as `<distribution>-<major_version>.yml`,
for example `debian-13.yml`, `ubuntu-24.yml`, or `rocky-10.yml`. If the file
does not exist for a host, no distro-specific task is included. The playbooks
set `molecule_distro_specific_phase` so a distro file can choose whether a task
runs during `prepare`, `converge-before-support-roles`,
`converge-before-role`, `converge-after-role`, or `verify`.

`MOLECULE_DISTRO` still follows the Docker image name. For Rocky Linux 10, use
`MOLECULE_DISTRO=rockylinux10`; Ansible facts will still include
`distro-specifics/rocky-10.yml`.

## Moodle versions tested

The default scenario tests `MOODLE_405_STABLE` and expects a `4.5.` release.
This can be overridden with `MOODLE_VERSION` and `MOODLE_RELEASE_PREFIX`.

Debian 13 uses the same environment overrides, but defaults to
`MOODLE_500_STABLE` and a `5.0.` release because its default PHP version is not
supported by Moodle 4.5.


## Possible issues

### DNF mirrorlist errors on Rocky Linux 10 in CI

Rocky Linux 10 containers can occasionally fail package installs with:
```
Failed to download packages: No URLs in mirrorlist
```

The `prepare` phase now rewrites Rocky repo files to disable `mirrorlist` and
enable the static `baseurl` entries in `distro-specifics/rocky-10.yml`, which
avoids mirrorlist lookup failures in constrained CI environments.

### PAM account management errors on Rocky Linux 10 in CI

Rocky Linux 10 containers in GitHub Actions may fail with:
```
sudo: PAM account management error: Authentication service cannot retrieve authentication info
```

**Cause**: In restricted GitHub Actions runner environments, PAM services like
`pam_systemd.so` cannot access `systemd-logind`, causing sudo to fail during
account management phase even when running as root.

**Fix**: The prepare phase patches `/etc/pam.d/sudo` to add `pam_permit.so`,
which provides a sufficient but quick pass-through for account checks. This works
in both local Docker (where systemd-logind is available) and CI (where it isn't).

See `molecule/default/distro-specifics/rocky-10.yml`.

If you still need troubleshooting output, set `MOLECULE_VERIFY_DEBUG=1` before
running `molecule verify` to include the verbose diagnostics from
`molecule/default/tasks/verify-debug.yml`.

### AppArmor and php-fpm

`php-fpm` can hit a similar AppArmor restriction to the MySQL case on some
hosts, but not all host configurations are affected. For that reason, the
workaround is applied on the host in CI rather than baked into the Molecule
scenario itself.

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
