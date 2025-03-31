output "grafana_host_ips" {
  value = openstack_compute_instance_v2.grafana.*.access_ip_v4
}

output "chatops_host_ips" {
  value = openstack_compute_instance_v2.chatops.*.access_ip_v4
}

output "prometheus_host_ips" {
  value = openstack_compute_instance_v2.prometheus.*.access_ip_v4
}