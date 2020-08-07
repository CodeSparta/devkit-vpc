output "vpc_id" {
  value = aws_vpc.cluster_vpc.id
}

output "vpc_cidrs" {
  value = data.aws_vpc.cluster_vpc.cidr_block
}


