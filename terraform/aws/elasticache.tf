resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = "redis-subnet-group"
  subnet_ids = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]

  tags = {
    Name = "redis-subnet-group"
  }
}

# Security group for allowing all traffic to and from everywhere
resource "aws_security_group" "redis_sg" {
  name        = "redis_sg"
  description = "Allow traffic to Redis"
  vpc_id      = aws_vpc.ce_vpc.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # TODO Allow traffic from within the VPC
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "redis-sg"
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
  security_group_ids   = [aws_security_group.redis_sg.id]

  tags = {
    Name = "redis-cluster"
  }
}
