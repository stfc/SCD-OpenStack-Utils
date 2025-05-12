output "grafana_host_ips" {
  value = module.compute.grafana_host_ips
}

output "chatops_host_ips" {
  value = module.compute.chatops_host_ips
}

output "prometheus_host_ips" {
  value = module.compute.prometheus_host_ips
}

output "loadbalancer_host_ips" {
  value = var.floating_ip
}

output "loadbalancer_private_ip" {
  value = module.compute.loadbalancer_host_ip
}