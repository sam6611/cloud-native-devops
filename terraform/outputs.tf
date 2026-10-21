output "ecr_repository_urls" {
  description = "ECR repository URLs for all microservices"

  value = {
    for service, repository in aws_ecr_repository.services :
    service => repository.repository_url
  }
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API server endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "eks_cluster_ca_certificate" {
  description = "EKS cluster certificate authority data (base64)"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "eks_oidc_provider_url" {
  description = "EKS OIDC provider URL for IRSA"
  value       = aws_iam_openid_connect_provider.eks.url
}

output "eks_oidc_provider_arn" {
  description = "EKS OIDC provider ARN for IRSA trust policies"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "kubeconfig_command" {
  description = "Command to update local kubeconfig for EKS cluster access"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}"
}