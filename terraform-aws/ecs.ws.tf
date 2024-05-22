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
      image     = "620457613573.dkr.ecr.us-east-1.amazonaws.com/wschatengine:${var.image_tag_ws}"
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
      ]
    }
  ])
}

resource "aws_ecs_service" "ce_ws_service" {
  name            = "wschatengine-service"
  cluster         = aws_ecs_cluster.ce_api_cluster.id
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
