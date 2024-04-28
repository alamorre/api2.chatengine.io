resource "kubernetes_deployment" "redis" {
  metadata {
    name = "redis-deployment"
    labels = {
      app = "redis"
    }
  }

  spec {
    replicas = 1 # Start with one small instance
    selector {
      match_labels = {
        app = "redis"
      }
    }
    template {
      metadata {
        labels = {
          app = "redis"
        }
      }
      spec {
        container {
          image = "redis:6.2.14-bookworm"
          name  = "redis"
          resources {
            requests = {
              cpu    = "100m"  # 100 millicpu request
              memory = "128Mi" # 128 MB memory request
            }
            limits = {
              cpu    = "200m"  # 200 millicpu limit
              memory = "256Mi" # 256 MB memory limit
            }
          }
          port {
            container_port = 6379
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "redis" {
  metadata {
    name = "redis"
  }
  spec {
    selector = {
      app = "redis"
    }
    port {
      port        = 6379
      target_port = 6379
    }
    type = "ClusterIP"
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "redis" {
  metadata {
    name = "redis-hpa"
  }
  spec {
    scale_target_ref {
      kind        = "Deployment"
      name        = "redis-deployment"
      api_version = "apps/v1"
    }
    min_replicas                      = 1
    max_replicas                      = 10
    target_cpu_utilization_percentage = 50
  }
}
