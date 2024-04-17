resource "kubernetes_secret" "app_secret" {
  metadata {
    name = "app-secret"
  }

  data = {
    "PIPELINE" = base64encode("production")
    # Add other secret data here
  }
}
