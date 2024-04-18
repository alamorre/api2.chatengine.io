variable "pipeline" {
  description = "The pipeline: local | production"
  type        = string
}

variable "secret_key" {
  description = "Django's Secret Key for DB salting"
  type        = string
}
