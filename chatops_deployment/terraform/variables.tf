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

variable "stack_volume_id" {
  type        = string
  description = "ID of the ChatOps Stack volume in your project."
}
