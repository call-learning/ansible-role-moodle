import json
from ansible.module_utils.basic import AnsibleModule

def main():
    module_args = dict(
        install_dir=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
        failed=False,
        moodle_is_installed=False,
        moodle_needs_upgrading=False,
        debug={},
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    install_dir = module.params['install_dir']
    config_file = f"{install_dir}/config.php"

    # Debugging: Add debug info
    result['debug']['install_dir'] = install_dir
    result['debug']['config_file'] = config_file

    # Step 1: Check if config.php exists using stat
    stat_cmd = f"ls {config_file}"  # Simple file listing
    rc, stdout, stderr = module.run_command(stat_cmd)

    # Add debug info for stat command
    result['debug']['stat_cmd'] = stat_cmd
    result['debug']['stat_stdout'] = stdout.strip()
    result['debug']['stat_stderr'] = stderr.strip()
    result['debug']['stat_rc'] = rc

    if rc != 0:
        result['msg'] = f"Config file not found in {install_dir}. Checked path: {config_file}."
        result['failed'] = True
        module.exit_json(**result)

    # Step 2: Run moodletool.php to check status
    moodletool_cmd = f"php {install_dir}/admin/cli/moodletool.php"
    rc, stdout, stderr = module.run_command(moodletool_cmd)

    result['debug']['moodletool_cmd'] = moodletool_cmd
    result['debug']['moodletool_stdout'] = stdout.strip()
    result['debug']['moodletool_stderr'] = stderr.strip()
    result['debug']['moodletool_rc'] = rc

    if rc != 0:
        result['msg'] = f"Error running Moodle CLI tool: {stderr.strip()}"
        result['failed'] = True
        module.exit_json(**result)

    # Step 3: Parse JSON output from Moodle CLI tool
    try:
        moodle_status = json.loads(stdout.strip())
    except json.JSONDecodeError as e:
        result['msg'] = f"Failed to parse JSON output from Moodle CLI tool: {str(e)}"
        result['debug']['raw_output'] = stdout.strip()
        result['failed'] = True
        module.exit_json(**result)

    # Merge parsed output into result
    result.update(moodle_status)
    if moodle_status.get('moodle_is_installed'):
        result['msg'] = "Moodle installation status retrieved successfully."
    else:
        result['msg'] = "Moodle is not installed."

    module.exit_json(**result)

if __name__ == '__main__':
    main()

