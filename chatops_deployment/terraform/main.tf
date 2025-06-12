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

module "networking" {
  source = "./modules/networking"

  deployment          = var.deployment
  external_network_id = var.external_network_id
}

module "compute" {
  source                = "./modules/compute"
  grafana_secgroup      = module.networking.grafana_secgroup
  chatops_secgroup      = module.networking.chatops_secgroup
  prometheus_secgroup   = module.networking.prometheus_secgroup
  elasticsearch_secgroup   = module.networking.elasticsearch_secgroup
  loadbalancer_secgroup = module.networking.loadbalancer_secgroup
  systemd_exporter_secgroup = module.networking.systemd_exporter_secgroup
  node_exporter_secgroup = module.networking.node_exporter_secgroup
  private_network       = module.networking.private_network
  private_subnet        = module.networking.private_subnet
  floating_ip           = var.floating_ip
  deployment            = var.deployment
  prometheus_volume_id = var.prometheus_volume_id
  elasticsearch_volume_id = var.elasticsearch_volume_id
  environment = var.environment
}