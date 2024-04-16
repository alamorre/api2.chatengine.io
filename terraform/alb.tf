# resource "aws_security_group" "alb_sg" {
#   name        = "ce-alb-sg"
#   description = "Security group for ALB"
#   vpc_id      = aws_vpc.main.id

#   ingress {
#     description = "HTTPS"
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   egress {
#     description = "Allow all outbound traffic"
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# resource "aws_lb" "app_lb" {
#   name               = "ce-app-lb"
#   internal           = false
#   load_balancer_type = "application"
#   security_groups    = [aws_security_group.alb_sg.id]
#   subnets            = [aws_subnet.subnet_1.id, aws_subnet.subnet_2.id]

#   enable_deletion_protection = false # TODO: Set to true for production
# }

# resource "aws_lb_target_group" "app_tg" {
#   name     = "app-tg"
#   port     = 80
#   protocol = "HTTP"
#   vpc_id   = aws_vpc.main.id

#   health_check {
#     protocol            = "HTTP"
#     path                = "/health"
#     matcher             = "200"
#     interval            = 30
#     timeout             = 5
#     healthy_threshold   = 5
#     unhealthy_threshold = 2
#   }
# }

# resource "aws_lb_listener" "https_listener" {
#   load_balancer_arn = aws_lb.app_lb.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-2016-08"
#   certificate_arn   = aws_acm_certificate.cert.arn

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.app_tg.arn
#   }
# }
