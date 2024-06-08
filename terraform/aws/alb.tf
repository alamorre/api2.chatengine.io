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

resource "aws_lb_target_group" "ce_ws_tg" {
  name        = "ws-target-group"
  port        = 9001
  protocol    = "HTTP"
  vpc_id      = aws_vpc.ce_vpc.id
  target_type = "ip" # Specify target type as IP

  health_check {
    path                = "/health/"
    port                = "9001"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name = "ws-target-group"
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

# rule to route /person/* to person-target-group
resource "aws_lb_listener_rule" "ce_ws_listener_rule" {
  listener_arn = aws_lb_listener.ce_api_listener.arn
  priority     = 90

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ce_ws_tg.arn
  }

  condition {
    path_pattern {
      values = ["/person_v4/*", "/chat/*"]
    }
  }
}

# rule to route /* to apichatengine-target-group
resource "aws_lb_listener_rule" "ce_api_listener_rule" {
  listener_arn = aws_lb_listener.ce_api_listener.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ce_api_tg.arn
  }

  condition {
    path_pattern {
      values = ["/*"]
    }
  }
}
