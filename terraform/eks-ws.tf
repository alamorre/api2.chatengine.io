variable "ws_pod_name" {
  description = "The name of the ws pod"
  type        = string
  default     = "ce-ws"
}

variable "ws_pod_label" {
  description = "The label to apply to ws pods"
  type        = string
  default     = "ce-ws"
}

resource "kubernetes_deployment" "ws_deployment" {
  metadata {
    name = var.ws_pod_name
    labels = {
      app = var.ws_pod_label
    }
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = var.ws_pod_label
      }
    }
    template {
      metadata {
        labels = {
          app = var.ws_pod_label
        }
      }
      spec {
        container {
          image = "620457613573.dkr.ecr.us-east-1.amazonaws.com/wschatengine:${var.image_tag_ws}"
          name  = var.ws_pod_name
          env_from {
            secret_ref {
              name = kubernetes_secret.app_secret.metadata[0].name
            }
          }
          port {
            container_port = 8080
          }
          resources {
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
        }
      }
    }

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_surge       = "100%" # Allow for 2x the resources when swapping
        max_unavailable = "25%"  # Allows up to 25% of the pods to be unavailable during the update
      }
    }
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "ws_hpa" {
  metadata {
    name      = "ce-ws-hpa"
    namespace = "default"
  }

  spec {
    min_replicas                      = 1
    max_replicas                      = 10
    target_cpu_utilization_percentage = 50
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.ws_deployment.metadata[0].name
    }
  }
}
