# EKS OIDC Provider for IRSA (IAM Roles for Service Accounts)
#
# IRSA allows Kubernetes ServiceAccounts to assume AWS IAM roles without
# embedding credentials in pods. The pod receives temporary credentials via
# the projected token volume mounted by EKS.
#
# Usage pattern:
#   1. Create an IAM role with trust policy referencing this OIDC provider.
#   2. Annotate the Kubernetes ServiceAccount:
#        eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/ROLE
#   3. The pod automatically receives short-lived AWS credentials.
#
# This is required for the AWS Load Balancer Controller, Cluster Autoscaler,
# and any application that needs AWS API access from within the cluster.

data "tls_certificate" "eks" {
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = {
    Name        = "${var.project_name}-eks-oidc"
    Environment = var.environment
    Project     = var.project_name
  }
}
