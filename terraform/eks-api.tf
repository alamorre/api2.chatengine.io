variable "cluster_name" {
  description = "The name of the EKS cluster"
  type        = string
  default     = "ce-cluster"
}

variable "pod_name" {
  description = "The name of the pod"
  type        = string
  default     = "ce-api"
}

variable "pod_label" {
  description = "The label to apply to api pods"
  type        = string
  default     = "ce-api"
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.29"

  cluster_endpoint_public_access = true

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.public_subnets

  # EKS Managed Node Group(s)
  eks_managed_node_group_defaults = {
    instance_types = ["t3.small"]
  }

  eks_managed_node_groups = {
    cluster_hpa = {
      min_size     = 1
      max_size     = 10
      desired_size = 1

      instance_types = ["t3.small"]
      capacity_type  = "SPOT"
    }
  }

  # Cluster access entry
  # To add the current caller identity as an administrator
  enable_cluster_creator_admin_permissions = true

  tags = {
    Environment = "prod"
    Terraform   = "true"
  }
}

resource "kubernetes_deployment" "ce_api" {
  metadata {
    name = var.pod_name
    labels = {
      app = var.pod_label
    }
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        app = var.pod_label
      }
    }
    template {
      metadata {
        labels = {
          app = var.pod_label
        }
      }
      spec {
        container {
          image = "620457613573.dkr.ecr.us-east-1.amazonaws.com/apichatengine:${var.image_tag}"
          name  = var.pod_name
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

resource "kubernetes_service" "cluster_lb" {
  depends_on = [aws_acm_certificate_validation.api_cert_validation]
  metadata {
    name = "ce-lb-service"
    annotations = {
      "service.beta.kubernetes.io/aws-load-balancer-backend-protocol" = "http"
      "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"         = aws_acm_certificate.api_cert.arn
      "service.beta.kubernetes.io/aws-load-balancer-ssl-ports"        = "443"
    }
  }
  spec {
    selector = {
      app = var.pod_label
    }
    port {
      name        = "https"
      port        = 443
      target_port = 8080
    }
    type = "LoadBalancer"
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "cluster_hpa" {
  metadata {
    name      = "cluster-hpa"
    namespace = "default"
  }

  spec {
    min_replicas                      = 3
    max_replicas                      = 10
    target_cpu_utilization_percentage = 50
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.ce_api.metadata[0].name
    }
  }
}

data "kubernetes_service" "cluster_lb" {
  metadata {
    name = kubernetes_service.cluster_lb.metadata[0].name
  }

  depends_on = [
    kubernetes_service.cluster_lb
  ]
}

resource "kubernetes_ingress_v1" "cluster_ingress" {
  metadata {
    name = "ce-api-ingress"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "true"
      "nginx.ingress.kubernetes.io/enable-cors"        = "true"
      "nginx.ingress.kubernetes.io/websocket-services" = "${kubernetes_service.cluster_lb.metadata[0].name}"
    }
  }

  spec {
    default_backend {
      service {
        name = kubernetes_service.cluster_lb.metadata[0].name
        port {
          number = kubernetes_service.cluster_lb.spec[0].port[0].port
        }
      }
    }

    rule {
      host = var.domain_name
      http {
        path {
          path = "/*"
          backend {
            service {
              name = kubernetes_service.cluster_lb.metadata[0].name
              port {
                number = kubernetes_service.cluster_lb.spec[0].port[0].port
              }
            }
          }
        }
      }
    }

    tls {
      hosts       = [var.domain_name]
      secret_name = "api2-chatengine-io-tls"
    }
  }
}
