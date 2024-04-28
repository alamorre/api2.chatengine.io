resource "kubernetes_secret" "app_secret" {
  metadata {
    name = "app-secret"
  }

  # Alphabetic order
  data = {
    # A
    "AWS_ACCESS_KEY_ID"       = var.aws_access_key_id
    "AWS_SECRET_ACCESS_KEY"   = var.aws_secret_access_key
    "AWS_STORAGE_BUCKET_NAME" = var.aws_storage_bucket_name
    # B
    "DB_NAME"    = var.db_name
    "DB_USER_NM" = var.db_username
    "DB_USER_PW" = var.db_password
    # P
    "PIPELINE" = var.pipeline
    # R
    "REDIS_HOST" = var.redis_host
    "REDIS_PORT" = var.redis_port
    # S
    "SECRET_KEY"               = var.secret_key
    "SEND_GRID_KEY"            = var.send_grid_key
    "SENTRY_DSN"               = var.sentry_dsn
    "STRIPE_KEY"               = var.stripe_key
    "STRIPE_LIGHT_PLAN"        = var.stripe_light_plan
    "STRIPE_PRODUCTION_PLAN"   = var.stripe_production_plan
    "STRIPE_PROFESSIONAL_PLAN" = var.stripe_professional_plan
    "STRIPE_TAX_RATE"          = var.stripe_tax_rate
  }
}
