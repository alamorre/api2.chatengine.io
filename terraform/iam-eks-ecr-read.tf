provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", var.cluster_name]
    command     = "aws"
  }
}

resource "aws_iam_policy" "ecr_read" {
  name        = "ce-ecr-read-policy"
  description = "Allows EKS to pull images from ECR"
  policy      = <<EOF
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability"
                ],
                "Resource": "*"
            }
        ]
    }
    EOF
}

resource "aws_iam_role" "eks_ecr_role" {
  name = "ce-eks-ecr-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "eks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_read_attach" {
  role       = aws_iam_role.eks_ecr_role.name
  policy_arn = aws_iam_policy.ecr_read.arn
}

resource "kubernetes_cluster_role_binding" "ecr_role_binding" {
  metadata {
    name = "ce-eks-ecr-role-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "system:node"
  }
  subject {
    kind      = "User"
    name      = aws_iam_role.eks_ecr_role.arn
    api_group = "rbac.authorization.k8s.io"
  }
}
