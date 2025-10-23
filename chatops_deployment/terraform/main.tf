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
  cloud = var.cloud
}

module "networking" {
  source = "./modules/networking"

  deployment          = var.deployment
  external_network_id = var.external_network_id
  cloud = var.cloud
}

module "compute" {
  source                = "./modules/compute"
  stack_secgroup = module.networking.stack_secgroup
  private_network       = module.networking.private_network
  private_subnet        = module.networking.private_subnet
  floating_ip           = var.floating_ip
  deployment            = var.deployment
  stack_volume_id = var.stack_volume_id
  environment = var.environment
  cloud = var.cloud
}
