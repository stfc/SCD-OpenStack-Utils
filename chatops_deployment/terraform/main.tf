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
  loadbalancer_secgroup = module.networking.loadbalancer_secgroup
  deployment            = var.deployment
  private_network       = module.networking.private_network
  floating_ip           = var.floating_ip
}