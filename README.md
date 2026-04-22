# Ansible Role: Moodle

[![CI Test](https://github.com/call-learning/ansible-role-moodle/actions/workflows/molecule.yml/badge.svg)](https://github.com/call-learning/ansible-role-moodle/actions/workflows/molecule.yml)
[![Lint](https://github.com/call-learning/ansible-role-moodle/actions/workflows/lint.yml/badge.svg)](https://github.com/call-learning/ansible-role-moodle/actions/workflows/lint.yml)

Installs and manages Moodle (4.3+) on Debian, Ubuntu, and Rocky Linux hosts.
Tested with Ansible 11 / ansible-core 2.18.

## Requirements

Use a supported host with PHP 8.1+, Apache 2.4, Git, and either PostgreSQL or MariaDB/MySQL available.
This role manages Moodle itself; the surrounding web and database stack should be prepared separately.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
moodle_version: "MOODLE_403_STABLE"
moodle_src_path: "/srv/moodle/src"
moodle_domain_name: "moodle.test"
moodle_is_https: false

moodle_database:
  dbtype: "pgsql"
  dbhost: "localhost"
  dbname: "moodle"
  dbuser: "username"
  dbpass: "password"
  dbprefix: "mdl_"

moodle_run_config: true
moodle_manage_config: true
moodle_overwrite_config: false
moodle_fetch_source: true
moodle_reset_admin_password: false
php_set_default_cli: false
php_package_strategy: "versioned"
```

Important behavior:

- `moodle_fetch_source`: fetch or update the Moodle git checkout.
- `moodle_run_config`: run installation and upgrade orchestration.
- `moodle_manage_config`: create `config.php` when missing.
- `moodle_overwrite_config`: update an existing `config.php`. Keep this `false` unless you explicitly want the role to rewrite a live site's configuration.
- `moodle_reset_admin_password`: reset the admin password on an existing installation.
- `php_set_default_cli`: opt in to making the selected `php_version` the host default `php` command. Use this only after PHP packages are installed.
- `php_package_strategy`: applies to `tasks/phpsql-setup.yml` on Debian/Ubuntu. Use `versioned` for `php{{ php_version }}-*` packages, or `native` for distro-default `php-*` packages.
- `tasks/php-runtime-facts.yml`: if `php_package_strategy: "native"` and `php_version` is unset, the role derives `php_version` from the host distribution before exposing the PHP runtime facts.

When you import `tasks/php-runtime-facts.yml` or `tasks/phpsql-setup.yml`, the role exposes helper facts that other playbooks can consume directly:

- `php_cli_bin`
- `php_cli_versioned_bin`
- `php_fpm_service_name`
- `php_fpm_config_dir`
- `php_fpm_main_config_file`
- `php_fpm_pool_dir`
- `php_fpm_ini_file`

If you want to switch the host default `php` command after installation, call the dedicated task file explicitly:

```yaml
- import_role:
    name: call_learning.moodle
    tasks_from: php-runtime-facts

- import_role:
    name: call_learning.moodle
    tasks_from: phpsql-setup

- role: geerlingguy.php

- import_role:
    name: call_learning.moodle
    tasks_from: php-default-cli
  when: php_set_default_cli | bool
```

For native distro packages, this lets you avoid carrying a distribution-specific `php_version` expression in your playbook:

```yaml
vars:
  php_package_strategy: "native"

pre_tasks:
  - import_role:
      name: call_learning.moodle
      tasks_from: php-runtime-facts
```

## Dependencies

No hard role dependencies are declared.
If you want Ansible to provision the full stack, pair this role with infrastructure roles such as:

- `geerlingguy.apache`
- `geerlingguy.php`
- `geerlingguy.postgresql`
- `geerlingguy.mysql`

## Example Playbook

```yaml
- hosts: moodle
  become: true
  roles:
    - role: call_learning.moodle
      vars:
        moodle_domain_name: "moodle.example.com"
        moodle_is_https: true
        moodle_version: "MOODLE_405_STABLE"
        moodle_database:
          dbtype: "pgsql"
          dbhost: "127.0.0.1"
          dbname: "moodle"
          dbuser: "moodle"
          dbpass: "{{ vault_moodle_dbpass }}"
          dbprefix: "mdl_"
```

## License

MIT / BSD

## Author Information

This role was created in 2017 by [Laurent David](https://github.com/laurentdavid), from 
[Jeff Geerling](https://www.jeffgeerling.com/) roles templates author of 
[Ansible for DevOps](https://www.ansiblefordevops.com/).

## Testing

### Prerequisites

You must have the following installed:

- `ansible`
- `molecule`

The test suite is built around [Molecule](https://ansible.readthedocs.io/projects/molecule/).
GitHub Actions runs linting and Molecule scenarios on each change.

Run the default scenario with:

```bash
molecule test
```

Run a specific scenario with:

```bash
molecule test -s default
```
