import subprocess
import sys

from nose.tools import assert_true

USUAL_ANSWERS = {
    'php -v': [
        'OK',
        {
            'returncode': 1,
            'output':
                'PHP 7.2.28-3+ubuntu16.04.1+deb.sury.org+1'
        }
    ],
    'moosh -h': [
        'OK',
        {
            'returncode': 1,
            'output':
                ''
        },
    ],
}


def test_check_php_not_installed():
    moodlecheck = CheckMoodle("/var/www/moodle/")
    subprocessval = {'php -v': [
        'CallProcessError',
        {
            'returncode': 255,
            'output':
                'PHP 7.2.28-3+ubuntu16.04.1+deb.sury.org+1'
        }
    ],
    }
    moodlecheck._subprocess = MockedSuprocess(subprocessval)
    retvalue = moodlecheck.check()
    expectedvalue = {
        'failed': True,
        'msg': "Requirements not present (phpcli): php -v (255) : "
               "PHP 7.2.28-3+ubuntu16.04.1+deb.sury.org+1",
        'code': 'phpclinotinstalled'
    }
    assert_true(
        retvalue == expectedvalue
    )


def test_check_wrong_moodle_path():
    moodlecheck = CheckMoodle("/var/www/moodle/")
    mooshinfoanswer = {'moosh info': [
        'CallProcessError',
        {
            'returncode': 1,
            'output':
                'Could not find Moodle installation!'
        }
    ]
    }
    subprocessval = USUAL_ANSWERS.copy()
    subprocessval.update(mooshinfoanswer)
    moodlecheck._subprocess = MockedSuprocess(subprocessval)
    retvalue = moodlecheck.check()
    expectedvalue = {
        'failed': True,
        'msg': 'Invalid moodle source path',
        'code': 'invalidsourcepath'
    }
    assert_true(
        retvalue == expectedvalue
    )


def test_check_moodle_moosh_fail():
    moodlecheck = CheckMoodle("/var/www/moodle/")
    moodlecheck._skipfoldercheck = True  # We skip folder check here

    mooshinfoanswer = {
        'moosh info': [
            'CallProcessError',
            {
                'returncode': 1,
                'output':
                    'Error code: dbconnectionfailed'
            }
        ],
    }
    subprocessval = USUAL_ANSWERS.copy()
    subprocessval.update(mooshinfoanswer)
    moodlecheck._subprocess = MockedSuprocess(subprocessval)
    retvalue = moodlecheck.check()
    expectedvalue = {
        'failed': True,
        'msg': 'Error code: dbconnectionfailed',
        'code': 'mooshgeneralerror',
        'moodle_is_installed': False,
        'moodle_needs_upgrading': False,
        'current_version': None,
        'current_release': None}
    assert_true(
        retvalue == expectedvalue
    )


def test_check_moodle_needs_upgrading():
    moodlecheck = CheckMoodle("/var/www/moodle/")
    moodlecheck._skipfoldercheck = True  # We skip folder check here

    mooshinfoanswer = {
        'moosh info': [
            'Ok',
            {
                'returncode': 0,
                'output':
                    'Ok'
            }
        ],
        'moosh config-get moodle version': [
            'Ok',
            {
                'returncode': 0,
                'output': '2019111800.07'
            }
        ],
        'moosh config-get moodle release': [
            'Ok',
            {
                'returncode': 0,
                'output': '3.8+ (Build: 20200103)'
            }
        ],
        'moosh check-needsupgrade': [
            'Ok',
            {
                'returncode': 0,
                'output': '1'
            }
        ],

    }
    subprocessval = USUAL_ANSWERS.copy()
    subprocessval.update(mooshinfoanswer)
    moodlecheck._subprocess = MockedSuprocess(subprocessval)
    retvalue = moodlecheck.check()
    expectedvalue = {
        'failed': False,
        'msg': None,
        'code': None,
        'moodle_is_installed': True,
        'moodle_needs_upgrading': True,
        'current_version': '2019111800.07',
        'current_release': '3.8+ (Build: 20200103)'
    }
    assert_true(
        retvalue == expectedvalue
    )


def test_check_moodle_needs_installing():
    moodlecheck = CheckMoodle("/var/www/moodle/")
    moodlecheck._skipfoldercheck = True  # We skip folder check here

    mooshinfoanswer = {
        'moosh info': [
            'CallProcessError',
            {
                'returncode': 1,
                'output':
                    'Error: No admin account was found'
            },
        ],
    }
    subprocessval = USUAL_ANSWERS.copy()
    subprocessval.update(mooshinfoanswer)
    moodlecheck._subprocess = MockedSuprocess(subprocessval)
    retvalue = moodlecheck.check()
    expectedvalue = {
        'failed': False,
        'msg': 'Error: No admin account was found',
        'code': 'moodlenotinstalled',
        'moodle_is_installed': False,
        'moodle_needs_upgrading': False,
        'current_version': None,
        'current_release': None}
    assert_true(
        retvalue == expectedvalue
    )
