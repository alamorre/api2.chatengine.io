resource "aws_acm_certificate" "api_cert" {
  domain_name       = var.domain_name
  validation_method = "DNS"
  tags = {
    Environment = "production"
  }
}

resource "aws_route53_record" "api_cert_validation" {
  name    = tolist(aws_acm_certificate.api_cert.domain_validation_options)[0].resource_record_name
  type    = tolist(aws_acm_certificate.api_cert.domain_validation_options)[0].resource_record_type
  records = [tolist(aws_acm_certificate.api_cert.domain_validation_options)[0].resource_record_value]
  ttl     = 60

  zone_id = var.zone_id
}

resource "aws_acm_certificate_validation" "api_cert_validation" {
  certificate_arn         = aws_acm_certificate.api_cert.arn
  validation_record_fqdns = [aws_route53_record.api_cert_validation.fqdn]
}

resource "aws_route53_record" "api_record" {
  zone_id    = var.zone_id
  name       = var.domain_name
  type       = "CNAME"
  ttl        = "300"
  records    = [data.kubernetes_service.cluster_lb.status.0.load_balancer.0.ingress.0.hostname]
  depends_on = [kubernetes_service.cluster_lb]
}
