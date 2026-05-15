# Ansible Role: Moodle

[![CI](https://github.com/call-learning/ansible-role-moodle/actions/workflows/ci.yml/badge.svg)](https://github.com/call-learning/ansible-role-moodle/actions/workflows/ci.yml)

Installs and manages Moodle (4.5+) on Debian, Ubuntu, and Rocky Linux 10 hosts.
Tested with Ansible 13 / ansible-core 2.20.

## Requirements

Use a supported host with PHP 8.1+, Apache 2.4, Git, and either PostgreSQL or MariaDB/MySQL available.
This role manages Moodle itself; the surrounding web and database stack should be prepared separately.

On Debian-based systems, `php-fpm` can also be blocked by AppArmor depending on
the target path you use for `moodle_src_path` and the Moodle data directories.
If you deploy outside the default `/srv/moodle/...` layout, make sure the local
AppArmor policy allows PHP-FPM to read and write the target directories.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
moodle_version: "MOODLE_405_STABLE"
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
```

Important behavior:

- `moodle_fetch_source`: fetch or update the Moodle git checkout.
- `moodle_run_config`: run installation and upgrade orchestration.
- `moodle_manage_config`: create `config.php` when missing.
- `moodle_overwrite_config`: update an existing `config.php`. Keep this `false` unless you explicitly want the role to rewrite a live site's configuration.
- `moodle_reset_admin_password`: reset the admin password on an existing installation.
- `php_set_default_cli`: opt in to making the selected `php_version` the host default `php` command on Debian/Ubuntu. Use this only after PHP packages are installed, and set `php_version` explicitly.

When you import `tasks/phpsql-setup.yml`, the role exposes helper facts that other playbooks can consume directly:

- `php_packages`

If you want to switch the host default `php` command after installation, call the dedicated task file explicitly:

```yaml
- import_role:
    name: call_learning.moodle
    tasks_from: phpsql-setup

- role: geerlingguy.php

- import_role:
    name: call_learning.moodle
    tasks_from: php-default-cli
  when: php_set_default_cli | bool
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

If you prefer `uv` instead of a system Python for local tooling, you can create a dedicated environment and install the test dependencies with it:

```bash
uv venv
source .venv/bin/activate
uv pip install ansible molecule
```

The test suite is built around [Molecule](https://ansible.readthedocs.io/projects/molecule/).
GitHub Actions runs linting and Molecule scenarios through the `ci.yml` workflow on pull requests, scheduled runs, and pushes to `master`.
That workflow runs the full Molecule scenario set on the supported LTS baseline, and the monthly/manual `module-moodle-edge.yml` workflow checks the edge Moodle branch controlled by the `MOODLE_EDGE_VERSION` repository variable (default `502`).
Both workflows install tooling through `uv sync --frozen`, so CI uses the same locked dependency set as local `uv` runs.

Run the default scenario with:

```bash
molecule test
```

Run a specific scenario with:

```bash
molecule test -s default
```
