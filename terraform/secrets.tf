resource "kubernetes_secret" "app_secret" {
  metadata {
    name = "app-secret"
  }

  data = {
    "PIPELINE"   = var.pipeline
    "SECRET_KEY" = var.secret_key
  }
}
