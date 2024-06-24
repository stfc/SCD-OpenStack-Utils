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

# States we will be using openstack
provider "openstack" {
  cloud = "openstack"
}

# Creates a private network
resource "openstack_networking_network_v2" "private_network" {
  name           = "${var.deployment_name}-private_network"
  admin_state_up = "true"
}

# Creates a subnet within our private network 
resource "openstack_networking_subnet_v2" "subnet" {
  name       = "${var.deployment_name}-subnet"
  network_id = openstack_networking_network_v2.private_network.id
  cidr       = "192.168.1.0/24"
  ip_version = 4
}

# Creates a router within our network
resource "openstack_networking_router_v2" "router" {
  name                = "${var.deployment_name}-router"
  external_network_id = var.external_network_id
}

# Connects the router to our subnet
resource "openstack_networking_router_interface_v2" "router_interface" {
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.subnet.id
}

# Create a load balancer and places it in the subnet we made earlier
resource "openstack_lb_loadbalancer_v2" "loadbalancer" {
  name = "${var.deployment_name}-loadbalancer"
  vip_subnet_id = openstack_networking_subnet_v2.subnet.id
  vip_address = var.floating_ip
}

# Creating the bastion vm to access the other vm's
resource "openstack_compute_instance_v2" "bastion" {
  name = "${var.deployment_name}-bastion"
  image_name = var.image_name
  flavor_name = var.flavor_name
  key_pair = var.key_pair

  network {
    uuid = openstack_networking_network_v2.private_network.id
  }
}

# Create a ssh listener for the bastion vm
resource "openstack_lb_listener_v2" "ssh_listener" {
  name = "${var.deployment_name}-bastion-ssh"
  protocol        = "TCP"
  protocol_port   = 22
  loadbalancer_id = openstack_lb_loadbalancer_v2.loadbalancer.id
  timeout_client_data = 600000
  timeout_member_connect = 600000
  timeout_member_data = 600000
}

# Create an ssh listener for the web servers
resource "openstack_lb_listener_v2" "web_server_listener" {
  name = "${var.deployment_name}-web_servers"
  protocol        = "TCP"
  protocol_port   = 80 
  loadbalancer_id = openstack_lb_loadbalancer_v2.loadbalancer.id
}

# Creating the ssh pool
resource "openstack_lb_pool_v2" "ssh_pool" {
  name = "${var.deployment_name}-ssh-pool"
  protocol    = "TCP"
  lb_method   = "SOURCE_IP"
  listener_id = openstack_lb_listener_v2.ssh_listener.id
}

# Creating a web_servers pool
resource "openstack_lb_pool_v2" "web_servers_pool" {
  name = "${var.deployment_name}-web_servers_pool"
  protocol    = "TCP"
  lb_method   = "SOURCE_IP"
  listener_id = openstack_lb_listener_v2.web_server_listener.id
}

# Adds the bastion to the ssh pool with the ssh listener
resource "openstack_lb_member_v2" "ssh_member" {
  pool_id       = openstack_lb_pool_v2.ssh_pool.id
  address       = openstack_compute_instance_v2.bastion.access_ip_v4
  protocol_port = 22
  depends_on = [ openstack_compute_instance_v2.bastion ]
}

# Creating the web_server member
resource "openstack_lb_member_v2" "web_server_member" {
  pool_id       = openstack_lb_pool_v2.web_servers_pool.id
  count = length(openstack_compute_instance_v2.vm)
  address = openstack_compute_instance_v2.vm[count.index].access_ip_v4
  protocol_port = 80 
}

# Create multiple vm's for web serving
resource "openstack_compute_instance_v2" "vm" {
  name = format("${var.deployment_name}-vm-%d", count.index)
  count = var.instances
  image_name = var.image_name
  flavor_name = var.flavor_name
  key_pair = var.key_pair 
  
  network {
    uuid = openstack_networking_network_v2.private_network.id
  }

  # Due to weird issue faced with terraform creating vm's before subnets are made
  depends_on = [ 
    openstack_networking_subnet_v2.subnet,
    openstack_lb_loadbalancer_v2.loadbalancer
  ]
}
