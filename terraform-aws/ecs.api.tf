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
