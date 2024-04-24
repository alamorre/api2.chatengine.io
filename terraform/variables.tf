variable "pipeline" {
  description = "The pipeline: local | production"
  type        = string
}

variable "secret_key" {
  description = "Django's Secret Key for DB salting"
  type        = string
}

variable "image_tag" {
  description = "The tag for the Docker image to use."
  type        = string
}

variable "db_name" {
  description = "The name of Postgres DB."
  type        = string
}

variable "db_username" {
  description = "The user name of Postgres DB."
  type        = string
}
variable "db_password" {
  description = "The user password of Postgres DB."
  type        = string
}

variable "domain_name" {
  description = "Domain name for the API"
  type        = string
  default     = "api2.chatengine.io"
}

variable "zone_id" {
  description = "Route53 Zone ID"
  type        = string
}
