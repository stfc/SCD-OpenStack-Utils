variable "external_network_id" {
  description = "The id of the external network to connect the router to"
  type = string
}

variable "floating_ip" {
  description = "The floating ip to attach to the load balancer to access the grafanas"
  type = string
}

variable "image_name" {
  description = "The name of the image you want to use for the instances"
  type = string
}

variable "flavor_name" {
  description = "The name of the flavour that will be used by the instances"
  type = string
}

variable "key_pair" {
  description = "The key pair to put on the bastion vm"
  type = string
}

variable "instances" {
  description = "The number of web instances wanted"
  type = number
  default = 1
}
