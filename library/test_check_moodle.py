import json
import subprocess

from check_moodle import CheckMoodle
from nose.tools import assert_false, assert_true, assert_raises


# Here we just test the behaviour of the function check_moodle and ignore
# the rest
class MockedCheckMoodle(CheckMoodle):
    __is_php_installed = False
    __moodle_check_return = ""

    def __init__(self, install_dir, php_installed=False, moosh_installed=False,
                 check_moodle_return=None):
        super(self.__class__, self).__init__(install_dir)
        self.__is_php_installed = php_installed
        self.__is_moosh_installed = moosh_installed
        self.__moodle_check_return = check_moodle_return

    def _check_php_cli_installed(self):
        if not self.__is_php_installed:
            raise subprocess.CalledProcessError(127, "php -v")

    def _check_moosh_installed(self):
        if not self.__is_moosh_installed:
            raise subprocess.CalledProcessError(127, "moosh -v")

    def _check_moodle(self):
        if self.__moodle_check_return:
            expectedreturnvalue = json.loads(self.__moodle_check_return)
            if expectedreturnvalue.get('error', False):
                raise AttributeError(self.__moodle_check_return.errormsg)
            else:
                return expectedreturnvalue
        return None


def test_check_php_not_installed():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/")
    with assert_raises(subprocess.CalledProcessError):
        moodlecheck.check_moodle()


def test_check_wrong_moodle_path():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/", True, True,
                                    '{"error":true,'
                                    '"errormsg":"Wrong Moodle Path",'
                                    '"current_version":"",'
                                    '"current_release":"",'
                                    '"moodle_need_upgrading":false}')
    with assert_raises(AttributeError):
        moodlecheck.check_moodle()


def test_check_moodle_not_installed():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/", True, True,
                                    '{"error":false,'
                                    '"errormsg":"",'
                                    '"current_version":"",'
                                    '"current_release":"",'
                                    '"moodle_need_upgrading":false,'
                                    '"moodle_is_installed":false}')
    retvalue = moodlecheck.check_moodle()
    assert_false(retvalue['moodle_is_installed'])


def test_check_moodle_needs_upgrading():
    moodlecheck = MockedCheckMoodle("/var/www/moodle/", True, True,
                                    '{"error":false,"errormsg":"",'
                                    '"current_version":"",'
                                    '"current_release":"",'
                                    '"moodle_need_upgrading":true,'
                                    '"moodle_is_installed":true}')
    retvalue = moodlecheck.check_moodle()
    assert_true(retvalue['moodle_need_upgrading'])
