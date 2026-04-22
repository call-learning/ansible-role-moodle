# coding: utf-8
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
import os
import json
import shlex

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

TOOL_FILENAME = 'moodletool.php'


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        """Handles transferring and executing the tool directly."""
        if task_vars is None:
            task_vars = {}

        self.TRANSFERS_FILES = True  # Ensure temp folder is created
        super().run(tmp, task_vars)

        remote_tmp = self._connection._shell.tmpdir
        remote_path = os.path.join(remote_tmp, TOOL_FILENAME)

        action_plugin_dir = os.path.dirname(__file__)
        tool_path = os.path.join(action_plugin_dir, TOOL_FILENAME)

        install_dir = self._task.args.get('install_dir', '')
        if os.path.isfile(tool_path):
            # Upload tool to remote machine
            self._transfer_file(tool_path, remote_path)

            # Fix permissions
            self._fixup_perms2([remote_path, remote_tmp])

            # Run the PHP script directly
            # Run the PHP script directly with install_dir argument
            quoted_install_dir = shlex.quote(install_dir)
            result = self._low_level_execute_command(
                f"php {shlex.quote(remote_path)} {quoted_install_dir}",
                sudoable=True)

            # Cleanup the tool after execution
            self._low_level_execute_command(f"rm -f {remote_path}")
            self.cleanup(True)

            # Return the result from execution
            # Try to parse the output as JSON
            moodle_output = result.get('stdout', '').strip()
            return_value = {
                "changed": False,
                "failed": False,
            }
            try:
                parsed_output = json.loads(moodle_output)
                if parsed_output.get('failed'):
                    return_value.update({
                        "failed": True,
                        "msg": parsed_output.get('msg')
                    })
                else:
                    return_value.update(parsed_output)
            except json.JSONDecodeError:
                return_value.update({
                    "failed": True,
                    "msg": "Failed to parse the output from the Moodle tool: " + moodle_output
                })
            return return_value
        else:
            raise AnsibleError(
                f"Failed to find the tool ({TOOL_FILENAME}) at path ({tool_path})"
            )
