variable "cluster_name" {
  description = "The name of the EKS cluster"
  type        = string
  default     = "ce-cluster"
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
    example = {
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

resource "kubernetes_deployment" "my_app" {
  metadata {
    name = "my-app"
    labels = {
      app = "myapp"
    }
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        app = "myapp"
      }
    }
    template {
      metadata {
        labels = {
          app = "myapp"
        }
      }
      spec {
        container {
          image = "620457613573.dkr.ecr.us-east-1.amazonaws.com/apichatengine:${var.image_tag}"
          name  = "my-app"
          env_from {
            secret_ref {
              name = kubernetes_secret.app_secret.metadata[0].name
            }
          }
          port {
            container_port = 8080
          }
          # Add resource requests and limits
          resources {
            requests = {
              cpu    = "500m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "1000m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "my_app_service" {
  depends_on = [aws_acm_certificate_validation.api_cert_validation]
  metadata {
    name = "my-app-service"
    annotations = {
      "service.beta.kubernetes.io/aws-load-balancer-backend-protocol" = "http"
      "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"         = aws_acm_certificate.api_cert.arn
      "service.beta.kubernetes.io/aws-load-balancer-ssl-ports"        = "443"
    }
  }
  spec {
    selector = {
      app = "myapp"
    }
    port {
      name        = "https"
      port        = 443
      target_port = 8080
    }
    type = "LoadBalancer"
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "example" {
  metadata {
    name      = "my-app-hpa"
    namespace = "default"
  }

  spec {
    min_replicas                      = 3
    max_replicas                      = 10
    target_cpu_utilization_percentage = 50
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = "my-app" # Make sure this matches your deployment name
    }
  }
}

data "kubernetes_service" "my_app_lb" {
  metadata {
    name = kubernetes_service.my_app_service.metadata[0].name
  }

  depends_on = [
    kubernetes_service.my_app_service
  ]
}


