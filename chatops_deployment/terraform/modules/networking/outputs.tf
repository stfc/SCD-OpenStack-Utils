output "grafana_secgroup" {
  value = openstack_networking_secgroup_v2.grafana
}

output "chatops_secgroup" {
  value = openstack_networking_secgroup_v2.chatops
}

output "prometheus_secgroup" {
  value = openstack_networking_secgroup_v2.prometheus
}

output "loadbalancer_secgroup" {
  value = openstack_networking_secgroup_v2.loadbalancer
}

output "private_network" {
  value = openstack_networking_network_v2.private_network
}

output "private_subnet" {
  value = openstack_networking_subnet_v2.subnet
}
