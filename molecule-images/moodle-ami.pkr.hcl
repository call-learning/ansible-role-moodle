packer {
   required_plugins {
    docker = {
      source  = "github.com/hashicorp/docker"
      version = "~> 1"
    }
    ansible = {
      source  = "github.com/hashicorp/ansible"
      version = "~> 1"
    }
  }
}
variable "ansible_connection" {
  type    = string
  default = "docker"
}

variable "ansible_host" {
  type    = string
  default = "packer_builder"
}

variable "changes_cmd" {
  type = string
}

variable "changes_volumes" {
  type = string
}

variable "docker_image_dbflavor" {
  type = string
}

variable "docker_image_type" {
  type = string
}

variable "docker_image_version" {
  type = string
}

locals {
  full_image_version = "${var.docker_image_type}${var.docker_image_version}"
}

source "docker" "autogenerated_1" {
  changes     = ["VOLUME  [${var.changes_volumes}]", "CMD [\"${var.changes_cmd}\"]"]
  commit      = true
  image       = "geerlingguy/docker-${local.full_image_version}-ansible:latest"
  run_command = ["-d", "-i", "-t", "-v", "/sys/fs/cgroup:/sys/fs/cgroup:ro", "--privileged", "--name", "${var.ansible_host}", "{{ .Image }}"]
}

build {
  sources = ["source.docker.autogenerated_1"]

  provisioner "ansible" {
    extra_arguments      = ["--extra-vars", "ansible_host=${var.ansible_host} ansible_connection=${var.ansible_connection}"]
    galaxy_file          = "./requirements.yml"
    galaxy_force_install = true
    playbook_file        = "ansible/playbook-${var.docker_image_dbflavor}.yml"
    user                 = "root"
  }

  post-processor "docker-tag" {
    repository = "calllearning/${var.docker_image_type}-${var.docker_image_dbflavor}-moodle-ansible"
    tags       = ["${var.docker_image_version}"]
  }
}