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


provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "helm_release" "nginx_ingress" {
  name       = "nginx-ingress"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = "default"

  set {
    name  = "controller.service.type"
    value = "ClusterIP"
  }

  # Deploys the NGINX Ingress Controller using Helm. This controller
  # manages external access to the services in a Kubernetes cluster,
  # typically HTTP. It provides load balancing, SSL termination,
  # and name-based virtual hosting.
}

resource "kubernetes_service" "ingress_lb" {
  depends_on = [aws_acm_certificate_validation.api_cert_validation]

  metadata {
    name = "nginx-ingress-lb"
    annotations = {
      "service.beta.kubernetes.io/aws-load-balancer-backend-protocol" = "http"
      "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"         = aws_acm_certificate.api_cert.arn
      "service.beta.kubernetes.io/aws-load-balancer-ssl-ports"        = "443"
    }
  }
  spec {
    type = "LoadBalancer"
    selector = {
      "app.kubernetes.io/name"     = "ingress-nginx"
      "app.kubernetes.io/instance" = "nginx-ingress"
    }
    port {
      port        = 443
      target_port = 80
    }
  }

  # Configures a LoadBalancer service to expose the NGINX Ingress Controller on port 443 with SSL termination.
  # Traffic on port 443 is received by this LoadBalancer, which terminates the SSL connection using the specified ACM certificate.
  # After decrypting the traffic, it is forwarded to port 80 of the NGINX Ingress Controller pods.
  # This setup enables secure HTTPS access to applications managed by the ingress controller, leveraging AWS's native load balancing features.
}

data "kubernetes_service" "ingress_lb" {
  metadata {
    name = kubernetes_service.ingress_lb.metadata[0].name
  }

  depends_on = [
    kubernetes_service.ingress_lb
  ]

  # Meta-data on the NGINX Ingress Controller LoadBalancer service.
  # Needed for linking the LoadBalancer to the Route 53 DNS record.
}

resource "kubernetes_ingress_v1" "ingress_policy" {
  metadata {
    name = "api-ingress"
    annotations = {
      "nginx.ingress.kubernetes.io/rewrite-target" = "/"
    }
  }

  spec {
    ingress_class_name = "nginx"
    rule {
      http {
        path {
          path      = "/ws/*"
          path_type = "Prefix"
          backend {
            service {
              name = "ce-ws-service"
              port {
                number = kubernetes_service.ws_service.spec[0].port[0].port
              }
            }
          }
        }
        path {
          path      = "/person/*"
          path_type = "Prefix"
          backend {
            service {
              name = "ce-ws-service"
              port {
                number = kubernetes_service.ws_service.spec[0].port[0].port
              }
            }
          }
        }
        path {
          path      = "/chat/*"
          path_type = "Prefix"
          backend {
            service {
              name = "ce-ws-service"
              port {
                number = kubernetes_service.ws_service.spec[0].port[0].port
              }
            }
          }
        }
        path {
          path      = "/(.*)"
          path_type = "Prefix"
          backend {
            service {
              name = "ce-api-service"
              port {
                number = kubernetes_service.api_service.spec[0].port[0].port
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

  # Configures an Ingress resource to route traffic to the API and WebSocket services based on the request path.
  # Automatically linked to the NGINX Ingress Controller LoadBalancer service.
}
