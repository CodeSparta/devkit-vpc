module "vpc" {
  source = "./vpc"

}

module "security-groups" {
  source = "./security-groups"

  vpc_id = module.vpc.vpc_id

}