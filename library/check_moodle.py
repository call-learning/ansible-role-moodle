#!/usr/bin/env python
import os
import subprocess
import json

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

    """ Check if PHP is installed. This should be a private method but stayed public for unit testing    
    """
    def do_check_php_cli_installed(self):
        subprocess.check_call(["php","-v"])

    """ Check if Moodle is installed and / or configured. This should be a private method but stayed public for unit testing    
    """
    def do_check_moodle(self):
        read, write = os.pipe()
        os.write(write, phpscript)
        os.close(write)
        output = subprocess.check_output(["php","--", "-m " + self.install_dir], stdin=read)
        return json.loads(output)

    """ Checks if mooodle is installed or not
    """
    def check_moodle(self):
        retvalue = {
            "fatalerror": False,
            "errormsg": "",
            "errorcode": "",
            "oldversion": False,
            "newversion": False,
            "moodle_needs_upgrading": False,
            "moodle_is_installed": False
        }

        try:
            # First check that we can use php cli
            self.do_check_php_cli_installed()
            # Secondly launch the moodlecheck script in PHP
            retvalue = self.do_check_moodle()

        except subprocess.CalledProcessError:
            retvalue["fatalerror"] = True
            retvalue["errormsg"] = CheckMoodle.error_php_not_present['msg']
            retvalue["errorcode"] = CheckMoodle.error_php_not_present['code']
        return retvalue

    # Error messages
    error_php_not_present = { "code": "phpclinotpresent", "msg": "PHP command CLI not present"}


def main():
    # Parsing argument file
    module = AnsibleModule(
        argument_spec = dict(
            install_dir = dict(required=True)
        )
    )
    install_dir = module.params.get('install_dir')

    chkmoodle = CheckMoodle(install_dir)
    retvalue = chkmoodle.check_moodle()

    # Error handling and JSON return
    if not(retvalue["fatalerror"]):
        module.exit_json(
                msg=retvalue["errormsg"],
                code=retvalue["errorcode"],
                moodle_needs_upgrading = retvalue["moodle_needs_upgrading"],
                moodle_is_installed = retvalue["moodle_is_installed"])
    else:
        module.fail_json(
                msg=retvalue["errormsg"],
                code = retvalue["errorcode"]
        )

phpscript = '''
<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * CLI script to check the status of Moodle.
 * @package     ansible-role-moodle
 * @copyright   2018 Laurent David <laurent@call-learning.fr>
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define('CLI_SCRIPT', true);

$options = getopt("m:", array('moodlepath'));

$returnvalue = new stdClass();
$returnvalue->fatalerror = false; // This type of error is the one we cannot recover from and is not due to the moodle setup
$returnvalue->errorcode = "";
$returnvalue->errormsg = "";
$returnvalue->oldversion = "";
$returnvalue->newversion = "";
$returnvalue->moodle_needs_upgrading = false;
$returnvalue->moodle_is_installed = false;

$moodlepath = array_key_exists('m', $options) ? $options['m'] : null;
$moodlepath = (is_null($moodlepath) && array_key_exists('moodlepath', $options)) ? $options['moodlepath'] : $moodlepath;

if (is_null($moodlepath)) {
    $returnvalue->fatalerror = true;
    $returnvalue->errorcode = "wrongmoodlepath";
    $returnvalue->errormsg = "Wrong Moodle Path Provided: cannot find a moodle installed here";
    print json_encode($returnvalue);
    exit(1);
}

// Check first if moodle is installed
$configpath = realpath($moodlepath . '/config.php');

if (!file_exists($configpath)) {
    $returnvalue->moodle_is_installed = false;
    print json_encode($returnvalue);
    exit(0);
}

// Now we are sure it is installed check it it needs upgrading
try {
    ini_set('display_errors', '0');
    ini_set('log_errors', 0);
    define('NO_DEBUG_DISPLAY', true); // Do not display error on the command line
    require_once($configpath);
    global $DB;

    if (!$DB->get_manager()->table_exists('config')) {
        print json_encode($returnvalue);
        exit(0);
    }

    require_once($CFG->libdir . '/adminlib.php');       // various admin-only functions
    require_once($CFG->libdir . '/upgradelib.php');     // general upgrade/install related functions
    require_once($CFG->libdir . '/environmentlib.php');

    require("$CFG->dirroot/version.php");       // defines $version, $release, $branch and $maturity
    $returnvalue->oldversion = "$CFG->release ($CFG->version)";
    $returnvalue->newversion = "$release ($version)";
    $returnvalue->moodle_needs_upgrading = moodle_needs_upgrading();
    $returnvalue->moodle_is_installed = true;
} catch (Exception $e) {
    $returnvalue->errorcode = $e->errorcode;
    $returnvalue->errormsg = $e->getMessage();
}
print json_encode($returnvalue);
exit(0);
'''

if __name__ == "__main__":
    main()
