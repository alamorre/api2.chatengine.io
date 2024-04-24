output "cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "The hostname of the EKS cluster for kubectl."
}

output "my_app_service_hostname" {
  value       = lookup(kubernetes_service.my_app_service.status.0.load_balancer.0.ingress.0, "hostname", "")
  description = "The hostname of the load balancer for the my-app service."
}
