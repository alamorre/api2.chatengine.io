# Create a security group for public postgres access
resource "aws_security_group" "db_sg" {
  name        = "ce-public-postgres-sg"
  description = "Allow public access to Postgres"
  vpc_id      = aws_vpc.ce_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # TODO change to internal SG
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# Create a DB subnet group
resource "aws_db_subnet_group" "aurora_subnet_group" {
  name       = "ec-aurora-subnet-group"
  subnet_ids = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
}

# Define database engine version as 12.14
variable "db_engine_version" {
  default = "12.14"
}

# Create an Aurora DB cluster
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier     = "ce-aurora-cluster"
  engine                 = "aurora-postgresql"
  engine_version         = var.db_engine_version
  master_username        = var.db_username
  master_password        = var.db_password
  database_name          = var.db_name
  db_subnet_group_name   = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids = [aws_security_group.db_sg.id] # TODO: swap to internal SG
  deletion_protection    = false
  skip_final_snapshot    = true
}

# Create an Aurora DB instance
resource "aws_rds_cluster_instance" "aurora_instance" {
  cluster_identifier  = aws_rds_cluster.aurora_cluster.id
  instance_class      = "db.t3.medium" # Specify your preferred instance class
  engine              = aws_rds_cluster.aurora_cluster.engine
  engine_version      = aws_rds_cluster.aurora_cluster.engine_version
  publicly_accessible = true
}
