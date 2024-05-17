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

resource "aws_subnet" "subnet1" {
  vpc_id                  = aws_vpc.ce_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "ce-public-subnet1"
  }
}

resource "aws_subnet" "subnet2" {
  vpc_id                  = aws_vpc.ce_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "ce-public-subnet2"
  }
}

resource "aws_route_table" "ce_route_table" {
  vpc_id = aws_vpc.ce_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.ce_igw.id
  }

  tags = {
    Name = "ce-route-table"
  }
}

resource "aws_route_table_association" "ce_rta1" {
  subnet_id      = aws_subnet.subnet1.id
  route_table_id = aws_route_table.ce_route_table.id
}

resource "aws_route_table_association" "ce_rta2" {
  subnet_id      = aws_subnet.subnet2.id
  route_table_id = aws_route_table.ce_route_table.id
}

resource "aws_security_group" "external_sg" {
  name        = "ce-external-sg"
  description = "Security group for HTTPS access"
  vpc_id      = aws_vpc.ce_vpc.id

  ingress {
    description = "Allow HTTPS inbound traffic"
    from_port   = 443
    to_port     = 443
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
    Name = "HTTPS (External) Security Group"
  }
}

resource "aws_security_group" "internal_sg" {
  name        = "ce-internal-sg"
  description = "Security group for internal networking"
  vpc_id      = aws_vpc.ce_vpc.id

  ingress {
    description = "Allow all inbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.ce_vpc.cidr_block] # restrict to aws_vpc IP ranges
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # -1 signifies all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "All (Internal) Security Group"
  }
}
