#!/usr/bin/env python3
import os
import re
import subprocess
import traceback
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule


class CheckMoodle(object):
    """This class will check if the moodle installed in the install_dir and
        conduct the following checks:
        - Check that PHP cli is installed (prerequisite)
        - The configuration file is present and we can connect to the database
        - The database has been installed/setup
        - Moodle needs to be updated
    """

    def __init__(self, install_dir):
        self.install_dir = install_dir
        self._subprocess = subprocess
        self._skipfoldercheck = False
        # Flag here to ignore some tests when unit testing

    def _check_php_cli_installed(self):
        """ Check if PHP is installed. This should be a private method but
            stayed public for unit testing
        """
        retvalue = {
            'failed': False,
            "msg": None,
            "code": None,
        }
        try:
            self._subprocess.check_call(["php", "-v"])
        except subprocess.CalledProcessError as e:
            retvalue['failed'] = True
            retvalue['msg'] = "Requirements not present (phpcli): {command} " \
                              "({errorcode}) : {output}" \
                .format(
                command=e.cmd,
                output=e.output,
                errorcode=str(e.returncode))
            retvalue['code'] = 'phpclinotinstalled'
        return retvalue

    def _check_moosh_installed(self):
        """ Check if Moosh is installed. This should be a private method but
            stayed public for unit testing
        """
        retvalue = {
            'failed': False,
            "msg": None,
            "code": None,
        }
        try:
            self._subprocess.check_call(["moosh", "-h"])
        except subprocess.CalledProcessError as e:
            if e.returncode != 10:
                retvalue['failed'] = True
                retvalue[
                    'msg'] = "Requirements not present (moosh): {command} " \
                             "({errorcode}) : {output}" \
                    .format(
                    command=e.cmd,
                    output=e.output,
                    errorcode=str(e.returncode))
            retvalue['code'] = 'mooshnotinstalled'
        return retvalue

    def _check_moodle_folder(self):
        retvalue = {
            'failed': False,
            "msg": None,
            "code": None,
        }
        if not self._skipfoldercheck:
            if not os.path.exists(self.install_dir):
                retvalue['failed'] = True
                retvalue['msg'] = 'Invalid moodle source path'
                retvalue['code'] = 'invalidsourcepath'
                return retvalue

            if not os.path.exists(
                    os.path.join(self.install_dir, 'version.php')):
                retvalue['failed'] = True
                retvalue['msg'] = 'No version.php found in this path'
                retvalue['code'] = 'noversionphp'
                return retvalue
        try:
            self._subprocess.check_output(
                ["moosh", "info"], cwd=self.install_dir)
            return retvalue
        except subprocess.CalledProcessError as e:
            # Code value of 1 means that it is still not installed
            # So we don't return an error
            output = self.__convert_output(e.output)  # Python 2 unicode or 3.6
            if e.returncode == 1 and \
                    'Could not find Moodle installation' in output:
                retvalue['failed'] = True
                retvalue['msg'] = e.output
                retvalue['code'] = 'mooshmoodleinstallnotpresent'

        return retvalue

    def _check_moodle(self):
        """ Check if Moodle is installed and / or configured.
        """

        retvalue = {
            'failed': False,
            "msg": None,
            "code": None,
            'moodle_is_installed': False,
            'moodle_needs_upgrading': False,
            'current_version': None,
            'current_release': None,
        }
        try:
            self._subprocess.check_output(
                ["moosh", "info"], cwd=self.install_dir)
        except subprocess.CalledProcessError as e:
            # Code value of 1 means that it is still not installed
            # So we don't return an error
            retvalue['msg'] = e.output
            output = self.__convert_output(e.output)  # Python 2 unicode or 3.6
            if e.returncode == 1 and \
                    'Error: No admin account was found' in output:
                retvalue['code'] = 'moodlenotinstalled'
                return retvalue
            else:
                retvalue['failed'] = True
                retvalue['code'] = 'mooshgeneralerror'
                return retvalue

        version = self._subprocess.check_output(
            ["moosh", "config-get", "moodle",
             "version"], cwd=self.install_dir)
        version = self.__convert_output(version)  # Python 2 unicode or 3.6
        if version and re.match(r"[0-9]+\.?[0-9]*", version):
            retvalue["current_version"] = version
            retvalue["moodle_is_installed"] = True
        else:
            retvalue['failed'] = True
            retvalue['msg'] = 'Current Moodle version not found'
            retvalue['code'] = 'noversionfound'
            return retvalue

        release = self._subprocess.check_output(
            ["moosh", "config-get", "moodle",
             "release"], cwd=self.install_dir)
        release = self.__convert_output(release)  # Python 2 unicode or 3.6
        if release and re.match(r"[0-9.]+.*\(Build: [0-9.+]+\)",
                                release):
            retvalue["current_release"] = release
        else:
            retvalue['failed'] = True
            retvalue['msg'] = 'Current Moodle release not found'
            retvalue['code'] = 'noreleasefound'
            return retvalue

        needsupgrade = self._subprocess.check_output(
            ["moosh", "check-needsupgrade"], cwd=self.install_dir)
        needsupgrade = self.__convert_output(needsupgrade)
        # Python 2 unicode or 3.6
        if needsupgrade and re.match(r'[01]$', needsupgrade):
            retvalue[
                "moodle_needs_upgrading"] = needsupgrade != '0'
        else:
            retvalue['failed'] = True
            retvalue['msg'] = 'Failed checking for upgrade'
            retvalue['code'] = 'failedcheckingupgrade'
            return retvalue

        return retvalue

    """ Check if requirements are present and fail module if not
    """

    def _check_requirements(self):
        # First check that we can use php cli
        retvalue = self._check_php_cli_installed()
        if retvalue.get('failed', False):
            return retvalue
        retvalue = self._check_moosh_installed()
        if retvalue.get('failed', False):
            return retvalue
        retvalue = self._check_moodle_folder()
        return retvalue

    """ Checks if mooodle is installed or not
    """

    def check(self):
        try:
            # First check that we can use php cli and other basic requirements
            retvalue = self._check_requirements()
            if retvalue.get('failed', False):
                return retvalue
            return self._check_moodle()
        except Exception as e:
            return ({
                'failed': True,
                'msg': "Error raised : ({message}\n{trace})".format(
                    message=str(e),
                    trace=traceback.format_exc()
                ),
                'code': "generalerror"
            })

    def __convert_output(self, output, strip=True):
        if strip:
            output = output.strip()
        try:
            output = to_text(output, errors='surrogate_or_strict')
        except UnicodeError:
            pass
        return output


def main():
    # Parsing argument file
    module = AnsibleModule(
        argument_spec=dict(
            install_dir=dict(required=True)
        ),
        supports_check_mode=True
    )
    install_dir = module.params.get('install_dir')

    chkmoodle = CheckMoodle(install_dir)
    retvalue = chkmoodle.check()
    if retvalue and not retvalue.get('failed', False):
        module.exit_json(**retvalue)
    else:
        module.fail_json(**retvalue)


if __name__ == "__main__":
    main()
