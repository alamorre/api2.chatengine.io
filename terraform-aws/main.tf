# Provider
provider "aws" {
  region = "us-east-1"
}

# ECS configuration

resource "aws_ecs_cluster" "ce_api_cluster" {
  name = "ce-api-cluster"
}

resource "aws_ecs_task_definition" "ce_api_td" {
  family                   = "apichatengine"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # Adjust based on your requirements
  memory                   = "512" # Adjust based on your requirements
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "apichatengine"
      image     = "620457613573.dkr.ecr.us-east-1.amazonaws.com/apichatengine:latest"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_cluster.redis_cluster.cache_nodes[0].address
        },
        {
          name  = "REDIS_PORT"
          value = tostring(aws_elasticache_cluster.redis_cluster.port)
        }
      ]
    }
  ])
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs_task_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Effect = "Allow"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_service" "ce_api_service" {
  name            = "apichatengine-service"
  cluster         = aws_ecs_cluster.ce_api_cluster.id
  task_definition = aws_ecs_task_definition.ce_api_td.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
    security_groups  = [aws_security_group.internal_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ce_api_tg.arn
    container_name   = "apichatengine"
    container_port   = 8080
  }

  depends_on = [aws_iam_role_policy_attachment.ecs_task_execution]
}


# Load balancer

resource "aws_lb" "ce_alb" {
  name               = "ce-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.external_sg.id]
  subnets            = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]

  tags = {
    Name = "ce-load-balancer"
  }
}

resource "aws_lb_target_group" "ce_api_tg" {
  name        = "apichatengine-target-group"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.ce_vpc.id
  target_type = "ip" # Specify target type as IP

  health_check {
    path                = "/health/"
    port                = "8080"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name = "apichatengine-target-group"
  }
}

resource "aws_lb_listener" "ce_api_listener" {
  load_balancer_arn = aws_lb.ce_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.api_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ce_api_tg.arn
  }
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
