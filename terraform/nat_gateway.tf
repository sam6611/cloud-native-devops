# NAT Gateway for private subnets.
#
# COST NOTE: A NAT Gateway charges ~$0.045/hr (~$1.08/day) plus ~$0.045/GB data processed.
# For development, this can be omitted if worker nodes are placed in public subnets
# (current node_group.tf uses public subnets for this reason).
# To enable NAT, uncomment this file AND update node_group.tf to use private subnet IDs.
#
# With private nodes you gain an important security benefit: worker EC2 instances are
# not directly reachable from the internet. Outbound traffic (ECR pulls, etc.) still
# works through the NAT.

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name        = "${var.project_name}-nat-eip"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id # NAT must be in a public subnet

  tags = {
    Name        = "${var.project_name}-nat-gw"
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [aws_internet_gateway.main]
}

resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main.id
}
