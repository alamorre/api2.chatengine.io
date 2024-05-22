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
      image     = "620457613573.dkr.ecr.us-east-1.amazonaws.com/apichatengine:${var.image_tag_api}"
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
          name  = "API_URL"
          value = var.api_url
        },
        {
          name  = "AWS_ACCESS_KEY_ID"
          value = var.aws_access_key_id
        },
        {
          name  = "AWS_SECRET_ACCESS_KEY"
          value = var.aws_secret_access_key
        },
        {
          name  = "AWS_STORAGE_BUCKET_NAME"
          value = var.aws_storage_bucket_name
        },
        {
          name  = "DB_HOST"
          value = aws_rds_cluster.aurora_cluster.endpoint
        },
        {
          name  = "DB_PORT"
          value = tostring(aws_rds_cluster.aurora_cluster.port)
        },
        {
          name  = "DB_NAME"
          value = var.db_name
        },
        {
          name  = "DB_USER_NM"
          value = var.db_username
        },
        {
          name  = "DB_USER_PW"
          value = var.db_password
        },
        {
          name  = "PIPELINE"
          value = var.pipeline
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_cluster.redis_cluster.cache_nodes[0].address
        },
        {
          name  = "REDIS_PORT"
          value = tostring(aws_elasticache_cluster.redis_cluster.port)
        },
        {
          name  = "SECRET_KEY"
          value = var.secret_key
        },
        {
          name  = "SEND_GRID_KEY"
          value = var.send_grid_key
        },
        {
          name  = "SENTRY_DSN_API"
          value = var.sentry_dsn_api
        },
        {
          name  = "STRIPE_KEY"
          value = var.stripe_key
        },
        {
          name  = "STRIPE_LIGHT_PLAN"
          value = var.stripe_light_plan
        },
        {
          name  = "STRIPE_PRODUCTION_PLAN"
          value = var.stripe_production_plan
        },
        {
          name  = "STRIPE_PROFESSIONAL_PLAN"
          value = var.stripe_professional_plan
        },
        {
          name  = "STRIPE_TAX_RATE"
          value = var.stripe_tax_rate
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/apichatengine"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "ce_api_log_group" {
  name              = "/ecs/apichatengine"
  retention_in_days = 1 # Adjust based on your log retention policy
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
