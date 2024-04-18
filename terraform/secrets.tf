resource "kubernetes_secret" "app_secret" {
  metadata {
    name = "app-secret"
  }

  data = {
    "PIPELINE" = "production"
  }
}
