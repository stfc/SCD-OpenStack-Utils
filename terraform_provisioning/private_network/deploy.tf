# Define required providers
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
  name           = "private_network"
  admin_state_up = "true"
}


resource "openstack_networking_subnet_v2" "subnet" {
  name       = "subnet"
  network_id = openstack_networking_network_v2.private_network.id
  cidr       = "10.0.0.0/24"
  ip_version = 4
}

resource "openstack_networking_router_v2" "router" {
  name                = "router"
  external_network_id = var.external_network_id 
}

resource "openstack_networking_router_interface_v2" "router_interface" {
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.subnet.id
}
