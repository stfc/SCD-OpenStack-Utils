variable "deployment" {
  type        = string
  description = "Name of the deployment"
}

variable "floating_ip" {
  type        = string
  description = "Floating IP to use for the service"
}

variable "external_network_id" {
  type        = string
  description = "ID of the external network in your project."
}

variable "elasticsearch_volume_id" {
  type        = string
  description = "ID of the elasticsearch volume in your project."
}
