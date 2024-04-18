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
  default     = "latest"  // You can set a default or require it to be passed explicitly.
}
