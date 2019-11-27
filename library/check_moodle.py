#!/usr/bin/env python
import os
import subprocess

from ansible.module_utils.basic import AnsibleModule


class CheckMoodle(object):
    """This class will check if the moodle installed in the install_dir and conduct the following checks:
        - Check that PHP cli is installed (prerequisite)
        - The configuration file is present and we can connect to the database
        - The database has been installed/setup
        - Moodle needs to be updated
    """

    def __init__(self, install_dir):
        self.install_dir = install_dir

    def _check_php_cli_installed(self):
        """ Check if PHP is installed. This should be a private method but stayed public for unit testing
        """
        subprocess.check_call(["php", "-v"])

    def _check_moosh_installed(self):
        """ Check if Moosh is installed. This should be a private method but stayed public for unit testing
        """
        try:
            subprocess.check_call(["moosh", "-h"])
        except subprocess.CalledProcessError as e:
            if e.returncode != 10:
                raise e  # Moosh returns a silly return code of 10 when no command provided

    def _check_moodle(self):
        """ Check if Moodle is installed and / or configured.
        """
        # Check first that the directory exists
        if not os.path.exists(self.install_dir): raise AttributeError('Invalid moodle source path')

        if not os.path.exists(os.path.join(self.install_dir, 'version.php')):
            raise AttributeError('No version.php found in this path')

        retvalue = {
            "current_version": False,
            "moodle_needs_upgrading": False,
            "moodle_is_installed": False
        }

        if not os.path.exists(os.path.join(self.install_dir, 'config.php')):
            return retvalue

        version = subprocess.check_output(["moosh", "-p", self.install_dir, "config-get", "moodle", "version"])
        if version:
            retvalue["current_version"] = version.strip()
        needsupgrade = subprocess.check_output(["moosh", "-p", self.install_dir, "check-needsupgrade"])
        if needsupgrade:
            retvalue["moodle_needs_upgrading"] = needsupgrade.strip() == '1'

        return retvalue

    """ Checks if mooodle is installed or not
    """

    def check_moodle(self):
        # First check that we can use php cli
        self._check_php_cli_installed()
        self._check_moosh_installed()
        # Secondly launch the moodlecheck script in PHP
        return self._check_moodle()


def main():
    # Parsing argument file
    module = AnsibleModule(
        argument_spec=dict(
            install_dir=dict(required=True)
        )
    )
    install_dir = module.params.get('install_dir')

    try:
        chkmoodle = CheckMoodle(install_dir)
        retvalue = chkmoodle.check_moodle()
        module.exit_json(
            msg="",
            code="",
            moodle_needs_upgrading=retvalue["moodle_needs_upgrading"],
            current_version=retvalue["current_version"],
            moodle_is_installed=retvalue["moodle_is_installed"])

    except subprocess.CalledProcessError as e:
        module.fail_json(
            msg="Requirements not present (phpcli or moosh): {command} ({errorcode}) : {output}"
                .format(command=e.cmd, output=e.output, errorcode=str(e.returncode)),
            code="phpcliormooshnotpresent"
        )
    except Exception as e:
        module.fail_json(
            msg=e.message,
            code="generalerror"
        )


if __name__ == "__main__":
    main()
