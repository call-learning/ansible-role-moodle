# coding: utf-8
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
import os
import json

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        # Get the install_dir parameter
        install_dir = self._task.args.get('install_dir')
        if not install_dir:
            return {'failed': True, 'msg': "The 'install_dir' parameter is required."}

        # Check first if there is a config.php file in the install_dir
        config_file = f"{install_dir}/config.php"
        # Check if the file exists on the remote host
        stat_result = self._execute_module(
            module_name='stat',
            module_args={'path': config_file},
            task_vars=task_vars or {}
        )
        # If the file doesn't exist, return a failure message
        if not stat_result.get('stat', {}).get('exists', False):
            return {
                'changed': False,
                'moodle_is_installed': False,
                'moodle_needs_upgrading': False,
                'msg': f"Could not find the config.php file at {config_file} on the remote host."
            }

        is_installed = False
        needs_upgrading = False
        # Command to run the Moodle CLI config script
        command = f"php {install_dir}/admin/cli/upgrade.php --is-pending"
        # Run the command on the remote host
        rc, stdout, stderr = self._connection.exec_command(command)

        # Check for command failure
        if rc == 2:
            needs_upgrading = True
        if rc == 1 and "Config table does not contain the version" in stderr.decode('utf-8'):
            return {
                'changed': False,
                'moodle_is_installed': is_installed,
                'moodle_needs_upgrading': needs_upgrading,
                'msg': "Moodle is not installed"
            }
        is_installed = True
        # Command to run the Moodle CLI config script
        command = f"php {install_dir}/admin/cli/cfg.php --json"

        # Run the command on the remote host
        rc, stdout, stderr = self._connection.exec_command(command)

        # Check for command failure
        if rc != 0:
            return {
                'failed': True,
                'msg': f"Command failed with error: {stderr.strip()}",
                'rc': rc
            }

        # Attempt to parse the JSON output
        try:
            parsed_output = json.loads(stdout.strip())
        except json.JSONDecodeError as e:
            return {
                'failed': True,
                'msg': f"Failed to parse JSON output: {str(e)}",
                'raw_output': stdout.strip()
            }
        current_version = parsed_output.get('version')
        current_release = parsed_output.get('release')
        # Return the parsed JSON output
        return {
            'changed': False,
            'config': parsed_output,
            'moodle_is_installed': is_installed,
            'moodle_needs_upgrading': needs_upgrading,
            'current_version': current_version,
            'current_release': current_release,
        }
