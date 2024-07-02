variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
}

variable "aws_storage_bucket_name" {
  description = "AWS Storage Bucket Name"
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
  description = "Domain Name"
  type        = string
}

variable "image_tag_api" {
  description = "The tag for the api.chatengine.io Docker image."
  type        = string
}

variable "image_tag_ws" {
  description = "The tag for the ws.chatengine.io Docker image."
  type        = string
}

variable "pipeline" {
  description = "The pipeline: local | production"
  type        = string
}

variable "redis_host" {
  description = "Redis Host"
  type        = string
}

variable "redis_port" {
  description = "Redis Port"
  type        = string
}

variable "secret_key" {
  description = "Django's Secret Key for DB salting"
  type        = string
}

variable "send_grid_key" {
  description = "SendGrid API Key"
  type        = string
}

variable "sentry_dsn_api" {
  description = "Sentry DSN for api.chatengine.io"
  type        = string
}

variable "sentry_dsn_ws" {
  description = "Sentry DSN for ws.chatengine.io"
  type        = string
}

variable "stripe_key" {
  description = "Stripe API Key"
  type        = string
}

variable "stripe_light_plan" {
  description = "Stripe Light Plan"
  type        = string
}

variable "stripe_production_plan" {
  description = "Stripe Production Plan"
  type        = string
}

variable "stripe_professional_plan" {
  description = "Stripe Professional Plan"
  type        = string
}

variable "stripe_tax_rate" {
  description = "Stripe Tax Rate"
  type        = string
}
variable "zone_id" {
  description = "Route53 Zone ID"
  type        = string
}
