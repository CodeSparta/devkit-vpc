module "vpc" {
  source = "./vpc"
  cluster_name = var.cluster_name
}

module "security-groups" {
  source = "./security-groups"

  vpc_id = module.vpc.vpc_id

}