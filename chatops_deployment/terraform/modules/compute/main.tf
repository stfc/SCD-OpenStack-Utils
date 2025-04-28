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
  cloud = "openstack"
}

resource "openstack_compute_keypair_v2" "bastion_keypair" {
  name       = "bastion-keypair-${var.deployment}"
  public_key = file("bastion-key.pub")
}

resource "openstack_compute_instance_v2" "grafana" {
  name            = "grafana-host-${var.deployment}"
  image_name      = "ubuntu-jammy-22.04-nogui"
  flavor_name     = "l3.nano"
  key_pair        = openstack_compute_keypair_v2.bastion_keypair.name
  security_groups = ["default", var.grafana_secgroup.name]
  count           = 2

  network {
    name = var.private_network.name
  }
  depends_on = [var.private_subnet]
}

resource "openstack_compute_instance_v2" "prometheus" {
  name            = "prometheus-host-${var.deployment}"
  image_name      = "ubuntu-jammy-22.04-nogui"
  flavor_name     = "l3.nano"
  key_pair        = openstack_compute_keypair_v2.bastion_keypair.name
  security_groups = ["default", var.prometheus_secgroup.name]

  network {
    name = var.private_network.name
  }
  depends_on = [var.private_subnet]
}

resource "openstack_compute_instance_v2" "elastic" {
  name            = "elasticsearch-host-${var.deployment}"
  image_name      = "ubuntu-jammy-22.04-nogui"
  flavor_name     = "l3.tiny"
  key_pair        = openstack_compute_keypair_v2.bastion_keypair.name
  security_groups = ["default", var.elasticsearch_secgroup.name]

  network {
    name = var.private_network.name
  }
  depends_on = [var.private_subnet]
}

resource "openstack_compute_volume_attach_v2" "prometheus_volume" {
  instance_id = openstack_compute_instance_v2.prometheus.id
  volume_id = var.prometheus_volume_id
}

resource "openstack_compute_volume_attach_v2" "elasticsearch_volume" {
  instance_id = openstack_compute_instance_v2.elastic.id
  volume_id = var.elasticsearch_volume_id
}

resource "openstack_compute_instance_v2" "chatops" {
  name            = "chatops-host-${var.deployment}"
  image_name      = "ubuntu-jammy-22.04-nogui"
  flavor_name     = "l3.nano"
  key_pair        = openstack_compute_keypair_v2.bastion_keypair.name
  security_groups = ["default", var.chatops_secgroup.name]
  count           = 3

  network {
    name = var.private_network.name
  }
  depends_on = [var.private_subnet]
}

resource "openstack_compute_instance_v2" "loadbalancer" {
  name            = "loadbalancer-host-${var.deployment}"
  image_name      = "ubuntu-jammy-22.04-nogui"
  flavor_name     = "l3.nano"
  key_pair        = openstack_compute_keypair_v2.bastion_keypair.name
  security_groups = ["default", var.loadbalancer_secgroup.name]

  network {
    name = var.private_network.name
  }
  depends_on = [var.private_subnet]
}

data "openstack_networking_port_v2" "loadbalancer_port" {
  fixed_ip   = openstack_compute_instance_v2.loadbalancer.network[0].fixed_ip_v4
  network_id = openstack_compute_instance_v2.loadbalancer.network[0].uuid
}

resource "openstack_networking_floatingip_associate_v2" "floating_ip" {
  floating_ip = var.floating_ip
  port_id     = data.openstack_networking_port_v2.loadbalancer_port.id
  depends_on  = [openstack_compute_instance_v2.loadbalancer]
}
