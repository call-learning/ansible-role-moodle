# Check Moodle state module

This module is intended to check Moodle state (installed, to be upgraded) so we can take decision regarding
what needs to be done in term of setting it up.

    - name: Moodle - Check the state of current moodle
      check_moodle:
        install_dir: "{{ moodle_src_path }}"
      register: moodle_state

The moodle_state will have the following values:

* msg: an error message if any (this contains the error message sent by moodle, for example if we cannot
connect to existing database)
* code: error code if any (from moodle)
* moodle_needs_upgrading: boolean - moodle needs upgrading
* moodle_is_installed: boolean - moodle is installed (a *valid* config file is there)

The process can also fail if the PHP CLI command (`php`) does not work or the provided folder is not a moodle folder.

## Testing 
To test it you need to install nose

    pip install nose
    
Then:

    cd library
    nosetests -v test_check_moodle.py
    
You can also test it using a mini test playbook:

    ansible-playbook -i 'localhost,' tests/test-check-moodle.yml 