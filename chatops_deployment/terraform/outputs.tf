output "loadbalancer_private_ip" {
  value = module.compute.loadbalancer_host_ip
}

output "prometheus_device" {
  value = module.compute.prometheus_device
}

output "elasticsearch_device" {
  value = module.compute.elasticsearch_device
}