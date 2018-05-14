#!/usr/bin/env python
import pwd
from ansible.module_utils.basic import AnsibleModule


class CheckMoodle:
    """This class will check if the moodle installed in the install_dir and conduct the following checks:
        - Check that dependencies are installed no php installed, libraries not installed, etc...)
        - The configuration file is present and we can connect to the database
        - The database has been installed
        - Moodle needs to be updated

    """
    def __init__(self, install_dir):
        self.install_dir = install_dir

    # Check if user exists
    def check_moodle(self):
        try:
            # First check that we can use php cli


        except KeyError:
            success = False
            ret_msg = 'User %s does not exists' % self.user
        return success, ret_msg, uid, gid

def main():
    # Parsing argument file
    module = AnsibleModule(
        argument_spec = dict(
            install_dir = dict(required=True)
        )
    )
    install_dir = module.params.get('install_dir')

    chkmoodle = CheckMoodle(install_dir)
    success, ret_msg, uid, gid = chkmoodle.check_moodle()

    # Error handling and JSON return
    if success:
        module.exit_json(msg=ret_msg, uid=uid, gid=gid)
    else:
        module.fail_json(msg=ret_msg)

if __name__ == "__main__":
    main()