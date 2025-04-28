output "grafana_host_ips" {
  value = openstack_compute_instance_v2.grafana.*.access_ip_v4
}

output "chatops_host_ips" {
  value = openstack_compute_instance_v2.chatops.*.access_ip_v4
}

output "prometheus_host_ips" {
  value = openstack_compute_instance_v2.prometheus.*.access_ip_v4
}

output "elastic_host_ips" {
  value = openstack_compute_instance_v2.elastic.*.access_ip_v4
}

output "loadbalancer_host_ip" {
  value = openstack_compute_instance_v2.loadbalancer.access_ip_v4
}

output "prometheus_device" {
  value = openstack_compute_volume_attach_v2.prometheus_volume.device
}

output "elasticsearch_device" {
  value = openstack_compute_volume_attach_v2.elasticsearch_volume.device
}