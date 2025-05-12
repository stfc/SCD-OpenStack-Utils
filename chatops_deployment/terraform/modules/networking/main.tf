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

resource "openstack_networking_secgroup_v2" "grafana" {
  name        = "grafana-${var.deployment}"
  description = "Grafana host security group."
}

resource "openstack_networking_secgroup_rule_v2" "grafana" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 3000
  port_range_max    = 3000
  remote_ip_prefix  = "192.168.100.0/22"
  security_group_id = openstack_networking_secgroup_v2.grafana.id
}

resource "openstack_networking_secgroup_v2" "chatops" {
  name        = "chatops-${var.deployment}"
  description = "ChatOps host security group."
}

resource "openstack_networking_secgroup_rule_v2" "chatops" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 3000
  port_range_max    = 3000
  remote_ip_prefix  = "192.168.100.0/22"
  security_group_id = openstack_networking_secgroup_v2.chatops.id
}

resource "openstack_networking_secgroup_rule_v2" "docker_metrics" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9323
  port_range_max    = 9323
  remote_ip_prefix  = "192.168.100.0/22"
  security_group_id = openstack_networking_secgroup_v2.chatops.id
}

resource "openstack_networking_secgroup_v2" "prometheus" {
  name        = "prometheus-${var.deployment}"
  description = "Prometheus host security group."
}

resource "openstack_networking_secgroup_rule_v2" "prometheus" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9090
  port_range_max    = 9090
  remote_ip_prefix  = "192.168.100.0/22"
  security_group_id = openstack_networking_secgroup_v2.prometheus.id
}

resource "openstack_networking_secgroup_v2" "loadbalancer" {
  name        = "loadbalancer-${var.deployment}"
  description = "Load balancer host security group."
}

resource "openstack_networking_secgroup_rule_v2" "loadbalancer_http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.loadbalancer.id
}

resource "openstack_networking_secgroup_rule_v2" "loadbalancer_https" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.loadbalancer.id
}

resource "openstack_networking_secgroup_rule_v2" "loadbalancer_prometheus" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8405
  port_range_max    = 8405
  remote_ip_prefix  = "192.168.100.0/22"
  security_group_id = openstack_networking_secgroup_v2.loadbalancer.id
}
