
# Request a certificate for the domain and its www subdomain
resource "aws_acm_certificate" "cert" {
  domain_name       = "api.lamorre.com"
  validation_method = "DNS"

  tags = {
    Name = "ce_api_certificate"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Declare the Route 53 zone for the domain
data "aws_route53_zone" "selected" {
  name = "lamorre.com"
}

# Define the Route 53 records for certificate validation
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = data.aws_route53_zone.selected.zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

resource "aws_route53_record" "api_record" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = "api.lamorre.com"
  type    = "CNAME"

  alias {
    name                   = aws_lb.app_lb.dns_name
    zone_id                = aws_lb.app_lb.zone_id
    evaluate_target_health = true
  }
}

# Define the certificate validation resource
resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}
