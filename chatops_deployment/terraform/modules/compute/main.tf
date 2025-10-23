terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

provider "openstack" {
  cloud = var.cloud
}

resource "openstack_compute_keypair_v2" "bastion_keypair" {
  name       = "bastion-keypair-${var.deployment}"
  public_key = file("${var.environment}-bastion-key.pub")
}

resource "openstack_compute_instance_v2" "stack" {
  name            = "chatops-stack-${var.deployment}"
  image_name      = "ubuntu-jammy-22.04-nogui"
  flavor_name     = "l3.micro"
  key_pair        = openstack_compute_keypair_v2.bastion_keypair.name
  security_groups = ["default", var.stack_secgroup.name]

  network {
    name = var.private_network.name
    fixed_ip_v4 = "192.168.100.100"
  }

  depends_on = [var.private_subnet]
}

resource "openstack_compute_volume_attach_v2" "stack_volume" {
  instance_id = openstack_compute_instance_v2.stack.id
  volume_id = var.stack_volume_id
}

data "openstack_networking_port_v2" "stack_port" {
  fixed_ip   = openstack_compute_instance_v2.stack.network[0].fixed_ip_v4
  network_id = openstack_compute_instance_v2.stack.network[0].uuid
}

resource "openstack_networking_floatingip_associate_v2" "floating_ip" {
  floating_ip = var.floating_ip
  port_id     = data.openstack_networking_port_v2.stack_port.id
  depends_on  = [openstack_compute_instance_v2.stack]
}
