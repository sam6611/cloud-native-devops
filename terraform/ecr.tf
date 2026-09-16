resource "aws_ecr_repository" "services" {
  for_each = toset([
    "user-service",
    "product-service",
    "order-service",
    "payment-service",
    "api-gateway"
  ])

  name                 = "${var.project_name}/${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}/${each.key}"
    Environment = var.environment
    Project     = var.project_name
    Service     = each.key
  }
}