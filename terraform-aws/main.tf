# Provider
provider "aws" {
  region = "us-east-1"
}

# VPC

resource "aws_vpc" "ce_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "ce-vpc"
  }
}

resource "aws_internet_gateway" "ce_igw" {
  vpc_id = aws_vpc.ce_vpc.id

  tags = {
    Name = "ce-internet-gateway"
  }
}

resource "aws_subnet" "my_subnet1" {
  vpc_id                  = aws_vpc.ce_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "my-public-subnet1"
  }
}

resource "aws_subnet" "my_subnet2" {
  vpc_id                  = aws_vpc.ce_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "my-public-subnet2"
  }
}

resource "aws_route_table" "my_route_table" {
  vpc_id = aws_vpc.ce_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.ce_igw.id
  }

  tags = {
    Name = "my-route-table"
  }
}

resource "aws_route_table_association" "my_rta1" {
  subnet_id      = aws_subnet.my_subnet1.id
  route_table_id = aws_route_table.my_route_table.id
}

resource "aws_route_table_association" "my_rta2" {
  subnet_id      = aws_subnet.my_subnet2.id
  route_table_id = aws_route_table.my_route_table.id
}

resource "aws_security_group" "http_sg" {
  name        = "http-sg"
  description = "Security group for HTTP access"
  vpc_id      = aws_vpc.ce_vpc.id

  ingress {
    description = "Allow HTTP inbound traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allows access from any IP
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # -1 signifies all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "HTTP Security Group"
  }
}

# ECS configuration

resource "aws_ecs_cluster" "nginx_cluster" {
  name = "nginx-cluster"
}

resource "aws_ecs_task_definition" "nginx" {
  family                   = "nginx"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # Adjust based on your requirements
  memory                   = "512" # Adjust based on your requirements
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "nginx"
      image     = "nginx:latest"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 80
          # hostPort      = 80
          protocol = "tcp"
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

resource "aws_ecs_service" "nginx_service" {
  name            = "nginx-service"
  cluster         = aws_ecs_cluster.nginx_cluster.id
  task_definition = aws_ecs_task_definition.nginx.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.my_subnet1.id, aws_subnet.my_subnet2.id]
    security_groups  = [aws_security_group.http_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.nginx_tg.arn
    container_name   = "nginx"
    container_port   = 80
  }

  depends_on = [aws_iam_role_policy_attachment.ecs_task_execution]
}


# Load balancer

resource "aws_lb" "nginx_alb" {
  name               = "nginx-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.http_sg.id]
  subnets            = [aws_subnet.my_subnet1.id, aws_subnet.my_subnet2.id]

  tags = {
    Name = "nginx-load-balancer"
  }
}

resource "aws_lb_target_group" "nginx_tg" {
  name        = "nginx-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.ce_vpc.id
  target_type = "ip" # Specify target type as IP

  health_check {
    path                = "/"
    port                = "80"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name = "nginx-target-group"
  }
}

resource "aws_lb_listener" "nginx_listener" {
  load_balancer_arn = aws_lb.nginx_alb.arn
  port              = 80
  protocol          = "HTTP"
  # port            = 443
  # protocol        = "HTTPS"
  # ssl_policy      = "ELBSecurityPolicy-2016-08"
  # certificate_arn = aws_acm_certificate.api_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.nginx_tg.arn
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
  type    = "CNAME"

  alias {
    name                   = aws_lb.nginx_alb.dns_name
    zone_id                = aws_lb.nginx_alb.zone_id
    evaluate_target_health = true
  }
}
