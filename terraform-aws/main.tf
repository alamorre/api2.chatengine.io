# Provider
provider "aws" {
  region = "us-east-1"
}

# Route53 and SSL

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

resource "aws_route53_record" "api_dns" {
  zone_id = var.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    # dualstack prefix is required for ALB
    name                   = "dualstack.${aws_lb.ce_alb.dns_name}"
    zone_id                = aws_lb.ce_alb.zone_id
    evaluate_target_health = true
  }
}

# ECR and permissions

resource "aws_iam_role_policy_attachment" "ecs_task_execution_ecr" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Elasticache on Redis

resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = "redis-subnet-group"
  subnet_ids = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]

  tags = {
    Name = "redis-subnet-group"
  }
}

resource "aws_elasticache_cluster" "redis_cluster" {
  cluster_id           = "redis-cluster"
  engine               = "redis"
  node_type            = "cache.t3.micro" # Adjust as needed
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet_group.name
  security_group_ids   = [aws_security_group.internal_sg.id]

  tags = {
    Name = "redis-cluster"
  }
}
