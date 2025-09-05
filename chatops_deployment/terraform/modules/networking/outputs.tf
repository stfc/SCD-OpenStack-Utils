output "stack_secgroup" {
  value = openstack_networking_secgroup_v2.stack
}

output "private_network" {
  value = openstack_networking_network_v2.private_network
}

output "private_subnet" {
  value = openstack_networking_subnet_v2.subnet
}
