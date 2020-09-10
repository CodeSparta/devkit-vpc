provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "./vpc"

  cluster_name = var.cluster_name
  cidr_blocks = var.cidr_blocks
  aws_region = var.aws_region
  default_tags = var.default_tags
  aws_azs = var.aws_azs
  vpc_private_subnet_cidrs = var.vpc_private_subnet_cidrs
  vpc_public_subnet_cidrs = var.vpc_public_subnet_cidrs
}
