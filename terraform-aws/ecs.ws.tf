resource "aws_ecs_task_definition" "ce_ws_td" {
  family                   = "wschatengine"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # Adjust based on your requirements
  memory                   = "512" # Adjust based on your requirements
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "wschatengine"
      image     = "992382606575.dkr.ecr.us-east-1.amazonaws.com/ws.chatengine.io:${var.image_tag_ws}"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 9001
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "API_URL"
          value = var.api_url
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
          name  = "SENTRY_DSN_WS"
          value = var.sentry_dsn_ws
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/wschatengine"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "ce_ws_log_group" {
  name              = "/ecs/wschatengine"
  retention_in_days = 1 # Adjust based on your log retention policy
}

resource "aws_ecs_service" "ce_ws_service" {
  name            = "wschatengine-service"
  cluster         = aws_ecs_cluster.ce_cluster.id
  task_definition = aws_ecs_task_definition.ce_ws_td.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
    security_groups  = [aws_security_group.internal_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ce_ws_tg.arn
    container_name   = "wschatengine"
    container_port   = 9001
  }

  depends_on = [aws_iam_role_policy_attachment.ecs_task_execution]
}

# Define CloudWatch Alarms for CPU and Memory utilization
resource "aws_cloudwatch_metric_alarm" "ws_cpu_high" {
  alarm_name          = "WSHighCPUUtilization"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "Alarm when CPU utilization exceeds 75%"
  dimensions = {
    ClusterName = aws_ecs_cluster.ce_cluster.id
    ServiceName = aws_ecs_service.ce_ws_service.name
  }
  alarm_actions = [aws_appautoscaling_policy.ws_scale_out.arn]
  ok_actions    = [aws_appautoscaling_policy.ws_scale_in.arn]
}

resource "aws_cloudwatch_metric_alarm" "ws_memory_high" {
  alarm_name          = "WSHighMemoryUtilization"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "Alarm when Memory utilization exceeds 75%"
  dimensions = {
    ClusterName = aws_ecs_cluster.ce_cluster.id
    ServiceName = aws_ecs_service.ce_ws_service.name
  }
  alarm_actions = [aws_appautoscaling_policy.ws_scale_out.arn]
  ok_actions    = [aws_appautoscaling_policy.ws_scale_in.arn]
}

# Create Application Auto Scaling Target
resource "aws_appautoscaling_target" "ecs_ws_target" {
  max_capacity       = 10
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.ce_cluster.id}/${aws_ecs_service.ce_ws_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Create Application Auto Scaling Policies
resource "aws_appautoscaling_policy" "ws_scale_out" {
  name               = "ws-scale-out"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_ws_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_ws_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_ws_target.service_namespace
  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60
    metric_aggregation_type = "Average"
    step_adjustment {
      scaling_adjustment          = 1
      metric_interval_lower_bound = 0
    }
  }
}

resource "aws_appautoscaling_policy" "ws_scale_in" {
  name               = "ws-scale-in"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_ws_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_ws_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_ws_target.service_namespace
  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60
    metric_aggregation_type = "Average"
    step_adjustment {
      scaling_adjustment          = -1
      metric_interval_upper_bound = 0
    }
  }
}
