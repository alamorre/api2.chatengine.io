resource "kubernetes_secret" "app_secret" {
  metadata {
    name = "app-secret"
  }

  data = {
    "PIPELINE"   = var.pipeline
    "SECRET_KEY" = var.secret_key
    "DB_NAME"    = var.db_name
    "DB_USER_NM" = var.db_username
    "DB_USER_PW" = var.db_password
  }
}
