# Moodle platform compatibility notes

This file summarizes which operating-system versions are likely to run recent Moodle versions **without changing default package versions**.

It is intended as a practical deployment note, not a substitute for checking the official Moodle requirements before a release or upgrade.

## Scope

This matrix is based on:

- Moodle versions: **4.5**, **5.0**, **5.1**, **5.2**
- Operating systems:
  - Ubuntu 22.04
  - Ubuntu 24.04
  - Debian 12
  - Debian 13
  - Rocky Linux 8
  - Rocky Linux 9
- Default distro package versions only

Assumption:

- **No external repositories**
- **No manual package upgrades/downgrades**
- **No custom PHP/MySQL/PostgreSQL packaging**

## Legend

- ✅ = works out of the box with stock packages
- ⚠️ = works only with a specific database choice, typically PostgreSQL instead of default MySQL/MariaDB
- ❌ = does not work without changing package versions or repository sources

## Moodle minimum version pattern

Across these Moodle versions, the main trend is:

| Moodle | PHP | PostgreSQL | MySQL | MariaDB |
|---|---:|---:|---:|---:|
| 4.5 | 8.1+ | 13+ | 8.0+ | 10.6.7+ |
| 5.0 | 8.2+ | 14+ | 8.4+ | 10.11+ |
| 5.1 | 8.2+ | 15+ | 8.4+ | 10.11+ |
| 5.2 | 8.3+ | 16+ | 8.4+ | 10.11+ |

### Main observations

1. **PHP rises gradually**: 8.1 → 8.2 → 8.2 → 8.3
2. **PostgreSQL rises almost one major version per Moodle release**: 13 → 14 → 15 → 16
3. **MySQL becomes a blocker from Moodle 5.0 onward** because Moodle 5.x requires **MySQL 8.4+**, while many distros still ship **MySQL 8.0** by default
4. **MariaDB stays friendly on Debian** because Debian 12 already provides **MariaDB 10.11**

## Compatibility matrix

This table answers the practical question:

> Will this Moodle version run on this OS using stock packages only?

| Moodle \ OS | Ubuntu 22.04 | Ubuntu 24.04 | Debian 12 | Debian 13 | Rocky 8 | Rocky 9 |
|---|---:|---:|---:|---:|---:|---:|
| 4.5 | ✅ | ✅ | ✅ | ✅ | ❌ | ⚠️ |
| 5.0 | ❌ | ⚠️ | ✅ | ✅ | ❌ | ❌ |
| 5.1 | ❌ | ⚠️ | ✅ | ✅ | ❌ | ❌ |
| 5.2 | ❌ | ⚠️ | ❌ | ✅ | ❌ | ❌ |

## Interpretation by OS

### Ubuntu 22.04

Typical stock packages:

- PHP 8.1
- PostgreSQL 14
- MySQL 8.0

Implications:

- **Moodle 4.5**: ✅ works
- **Moodle 5.0+**: ❌ blocked mainly by PHP 8.1 and MySQL 8.0

Conclusion:

- Good for **4.5**
- Not suitable for **5.x** without package changes

### Ubuntu 24.04

Typical stock packages:

- PHP 8.3
- PostgreSQL 16
- MySQL 8.0

Implications:

- **Moodle 4.5**: ✅ works
- **Moodle 5.0 / 5.1**: ⚠️ works with PostgreSQL, not with stock MySQL
- **Moodle 5.2**: ⚠️ works with PostgreSQL, not with stock MySQL

Conclusion:

- Good choice for recent Moodle **if using PostgreSQL**
- Less convenient if the project standard is stock MySQL

### Debian 12

Typical stock packages:

- PHP 8.2
- PostgreSQL 15
- MariaDB 10.11

Implications:

- **Moodle 4.5**: ✅ works
- **Moodle 5.0**: ✅ works
- **Moodle 5.1**: ✅ works
- **Moodle 5.2**: ❌ blocked by PHP 8.2 and PostgreSQL 15

Conclusion:

- Best all-around option for **Moodle 5.0 / 5.1**
- Very convenient when using MariaDB

### Debian 13

Typical stock packages:

- PHP 8.4
- PostgreSQL 17
- MariaDB 11.x

Implications:

- **Moodle 4.5 → 5.2**: ✅ works across the board

Conclusion:

- Best option in this list for **future-proofing**

### Rocky Linux 8

Typical stock packages are too old by default.

Implications:

- **Moodle 4.5 → 5.2**: ❌ not suitable without changing streams/repos

Conclusion:

- Avoid for modern Moodle unless package customization is already accepted

### Rocky Linux 9

Default/base availability is closer, but still not a clean fit with stock packages.

Typical issues:

- PHP often needs stream selection for the right version
- MariaDB default is too old for Moodle 5.x
- MySQL 8.0 is too old for Moodle 5.x
- Base PostgreSQL is not sufficient for the higher Moodle 5.x requirements

Implications:

- **Moodle 4.5**: ⚠️ possible depending on chosen stack, but not a clean “defaults only” fit
- **Moodle 5.0+**: ❌ not suitable without stream/repo changes

Conclusion:

- Treat Rocky as a platform that requires package management decisions, not a zero-tweaking default

## Recommended default choices

If the goal is **minimum operational friction**:

- **Moodle 4.5**
  - Ubuntu 22.04
  - Debian 12
- **Moodle 5.0 / 5.1**
  - Debian 12
  - Debian 13
  - Ubuntu 24.04 with PostgreSQL
- **Moodle 5.2**
  - Debian 13
  - Ubuntu 24.04 with PostgreSQL

## Simple rule of thumb

- If you want **MySQL with stock distro packages**, recent Moodle versions become difficult quickly
- If you want **PostgreSQL with stock distro packages**, Ubuntu and Debian align much better with Moodle 5.x
- If you want the easiest path for **Moodle 5.0 and 5.1**, choose **Debian 12**
- If you want the easiest path for **Moodle 5.2 and later**, choose **Debian 13** or **Ubuntu 24.04 + PostgreSQL**

## Suggested update process

When a new Moodle release appears:

1. Update the **Moodle minimum version pattern** table
2. Check current default package versions for each target OS
3. Re-evaluate the matrix using this rule:
   - PHP must meet minimum
   - Database engine version must meet minimum
   - If either fails with stock packages, mark ❌
   - If only one DB engine fits, mark ⚠️ and note which one
4. Add a short note if an OS requires AppStreams, alternative repos, or manual package selection

## Optional project convention

If you want to keep this file low-maintenance, you can adopt a simple rule in the project docs:

> For Moodle 5.x deployments, prefer Debian or Ubuntu with PostgreSQL unless there is a strong reason to standardize on another stack.

## Notes

- This file is intentionally practical and conservative.
- Always verify final requirements against official Moodle documentation before production deployment.
- Distro package sets evolve, so this matrix should be reviewed before each major infrastructure or Moodle upgrade.
