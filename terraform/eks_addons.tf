# EKS Cluster Add-ons
#
# These add-ons are required for a functional EKS cluster:
#   - coredns:   In-cluster DNS resolution. Pods cannot resolve service names without it.
#   - kube-proxy: Maintains network rules for Kubernetes Services on each node.
#   - vpc-cni:   AWS VPC CNI plugin. Assigns VPC IP addresses to pods (required on EKS).
#
# All three use "LATEST" resolve_conflict_on_create to pull the version EKS recommends
# for the cluster version (1.33). Pin to a specific version after the first apply if
# you need reproducible upgrades.

resource "aws_eks_addon" "coredns" {
  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "coredns"
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = {
    Name        = "${var.project_name}-coredns"
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [aws_eks_node_group.main]
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "kube-proxy"
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = {
    Name        = "${var.project_name}-kube-proxy"
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [aws_eks_cluster.main]
}

resource "aws_eks_addon" "vpc_cni" {
  cluster_name                = aws_eks_cluster.main.name
  addon_name                  = "vpc-cni"
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = {
    Name        = "${var.project_name}-vpc-cni"
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [aws_eks_cluster.main]
}
