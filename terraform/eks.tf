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
}

resource "kubernetes_service" "nginx_ingress_lb" {
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
}

data "kubernetes_service" "nginx_ingress_lb" {
  metadata {
    name = kubernetes_service.nginx_ingress_lb.metadata[0].name
  }

  depends_on = [
    kubernetes_service.nginx_ingress_lb
  ]
}

resource "kubernetes_ingress_v1" "example" {
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
          path      = "/admin(/|$)(.*)"
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
}



# resource "kubernetes_service" "cluster_lb" {
# depends_on = [aws_acm_certificate_validation.api_cert_validation]
#   metadata {
#     name = "ce-lb-service"
# annotations = {
# "service.beta.kubernetes.io/aws-load-balancer-backend-protocol" = "http"
# "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"         = aws_acm_certificate.api_cert.arn
# "service.beta.kubernetes.io/aws-load-balancer-ssl-ports"        = "443"
# }
#   }
#   spec {
#     selector = {
#       app = var.api_pod_label
#     }
#     port {
#       name        = "https"
#       port        = 443
#       target_port = 8080
#     }
#     type = "LoadBalancer"
#   }
# }

# data "kubernetes_service" "cluster_lb" {
#   metadata {
#     name = kubernetes_service.cluster_lb.metadata[0].name
#   }

#   depends_on = [
#     kubernetes_service.cluster_lb
#   ]
# }

# resource "kubernetes_ingress_v1" "cluster_ingress" {
#   metadata {
#     name = "ce-api-ingress"
#     annotations = {
#       "kubernetes.io/ingress.class"                    = "nginx"
#       "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
#       "nginx.ingress.kubernetes.io/ssl-redirect"       = "true"
#       "nginx.ingress.kubernetes.io/enable-cors"        = "true"
#       "nginx.ingress.kubernetes.io/websocket-services" = "${kubernetes_service.cluster_lb.metadata[0].name}"
#     }
#   }

#   spec {
#     default_backend {
#       service {
#         name = kubernetes_service.cluster_lb.metadata[0].name
#         port {
#           number = kubernetes_service.cluster_lb.spec[0].port[0].port
#         }
#       }
#     }

#     rule {
#       host = var.domain_name
#       http {
#         path {
#           path = "/*"
#           backend {
#             service {
#               name = kubernetes_service.cluster_lb.metadata[0].name
#               port {
#                 number = kubernetes_service.cluster_lb.spec[0].port[0].port
#               }
#             }
#           }
#         }
#       }
#     }

# tls {
#   hosts       = [var.domain_name]
#   secret_name = "api2-chatengine-io-tls"
# }
#   }
# }
