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

resource "openstack_networking_network_v2" "private_network" {
  name           = "private-network-${var.deployment}"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "subnet" {
  name       = "subnet-${var.deployment}"
  network_id = openstack_networking_network_v2.private_network.id
  cidr       = "192.168.100.0/24"
  ip_version = 4
}

resource "openstack_networking_router_v2" "router" {
  name                = "router-${var.deployment}"
  admin_state_up      = true
  external_network_id = var.external_network_id
}

resource "openstack_networking_router_interface_v2" "router_interface" {
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.subnet.id
}

resource "openstack_networking_secgroup_v2" "stack" {
  name        = "chatops-stack-${var.deployment}"
  description = "ChatOps Stack host security group."
}

resource "openstack_networking_secgroup_rule_v2" "stack_http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.stack.id
}

resource "openstack_networking_secgroup_rule_v2" "stack_https" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.stack.id
}
