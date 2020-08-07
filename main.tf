provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region  = var.aws_region
}

module "vpc" {
  source = "./vpc"

}

module "security-groups" {
  source = "./security-groups"

  vpc_id = module.vpc.vpc_id

}