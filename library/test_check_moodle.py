from nose.tools import assert_equals, assert_false, assert_true
from check_moodle import CheckMoodle
import json
import subprocess

class MockedCheckMoodle(CheckMoodle):
    __is_php_installed = False
    __moodle_check_return = ""

    def __init__(self, install_dir, php_installed, check_moodle_return):
        super(self.__class__, self).__init__(install_dir)
        self.__is_php_installed = php_installed
        self.__moodle_check_return = check_moodle_return

    def do_check_php_cli_installed(self):
        if not self.__is_php_installed:
            raise subprocess.CalledProcessError(127, "php -v")

    def do_check_moodle(self):
        return json.loads(self.__moodle_check_return)


def test_check_php_not_installed():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/",False, "")
    retvalue = moodlecheck.check_moodle()
    assert_equals(retvalue['errorcode'], CheckMoodle.error_php_not_present['code'])

def test_check_wrong_moodle_path():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/",True,
                                    '{"error":true,"errorcode":"wrongmoodlepath","errormsg":"Wrong Moodle Path","oldversion":"","newversion":"","moodle_need_upgrading":false}')
    retvalue = moodlecheck.check_moodle()
    assert_equals(retvalue['errorcode'], "wrongmoodlepath")

def test_check_moodle_not_installed():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/",True,
                                    '{"error":false,"errorcode":"","errormsg":"","oldversion":"","newversion":"","moodle_need_upgrading":false,"moodle_is_installed":false}')
    retvalue = moodlecheck.check_moodle()
    assert_equals(retvalue['errorcode'], "")
    assert_false(retvalue['moodle_is_installed'])

def test_check_moodle_needs_upgrading():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/",True,
                                    '{"error":false,"errorcode":"","errormsg":"","oldversion":"","newversion":"","moodle_need_upgrading":true,"moodle_is_installed":true}')
    retvalue = moodlecheck.check_moodle()
    assert_equals(retvalue['errorcode'], "")
    assert_true(retvalue['moodle_need_upgrading'])
