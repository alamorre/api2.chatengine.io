variable "api_pod_name" {
  description = "The name of the pod"
  type        = string
  default     = "ce-api"
}

variable "api_pod_label" {
  description = "The label to apply to api pods"
  type        = string
  default     = "ce-api"
}

resource "kubernetes_deployment" "ce_api" {
  metadata {
    name = var.api_pod_name
    labels = {
      app = var.api_pod_label
    }
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = var.api_pod_label
      }
    }
    template {
      metadata {
        labels = {
          app = var.api_pod_label
        }
      }
      spec {
        container {
          image = "620457613573.dkr.ecr.us-east-1.amazonaws.com/apichatengine:${var.api_image_tag}"
          name  = var.api_pod_name
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


resource "kubernetes_horizontal_pod_autoscaler" "cluster_hpa" {
  metadata {
    name      = "cluster-hpa"
    namespace = "default"
  }

  spec {
    min_replicas                      = 1
    max_replicas                      = 10
    target_cpu_utilization_percentage = 50
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.ce_api.metadata[0].name
    }
  }
}
