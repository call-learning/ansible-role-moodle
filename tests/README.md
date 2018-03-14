# Ansible Role tests

Instruction and test scripts created originally by Jeff Geerling (https://github.com/geerlingguy)

To run the test playbook(s) in this directory:

  1. Install and start Docker.
  1. You can either use the test.sh already in this folder. Optionally you can download/update this script 
  Jeff Geerling's created) into `tests/test.sh`:
     - `wget -O tests/test.sh https://gist.githubusercontent.com/geerlingguy/73ef1e5ee45d8694570f334be385e181/raw/`
     - Make the test shim executable: `chmod +x tests/test.sh`.
  1. Run (from the role root directory) `distro=[distro] playbook=[playbook] ./tests/test.sh`

If you don't want the container to be automatically deleted after the test playbook is run, add the following environment variables: `cleanup=false container_id=$(date +%s)`
