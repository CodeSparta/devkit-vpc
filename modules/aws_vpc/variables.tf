variable "region" {
  type = string
  default = "us-gov-west-1"
}
variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}
variable "vpc_tags" {
  type    = map(string)
  default = {}
}
variable "default_tags" {
  type    = map(string)
  default = {}
}
variable "dns_support_enabled" {
  type    = bool
  default = true
}
variable "enable_dns_hostnames" {
  type    = bool
  default = true
}
variable "instance_tenancy" {
  type    = string
  default = "default"
}
variable "vpc_name" {
  type    = string
  default = ""
}
variable "cluster_name" {
  type    = string
  default = ""
}
# Network Variables
variable "create_public_subnets" {
  description = "Determine whether to create public subnets or not"
  type        = bool
  default     = true
}
variable "create_private_subnets" {
  description = "Determine whether to create private subnets or not"
  type        = bool
  default     = true
}
variable "map_public_ip_on_launch" {
  type    = bool
  default = true
}
variable "public_subnet_suffix" {
  description = "Suffix to append to public subnets name"
  type        = string
  default     = "public"
}
variable "private_subnet_suffix" {
  description = "Suffix to append to private subnets name"
  type        = string
  default     = "private"
}
variable "private_subnets" {
  type    = list(string)
  default = []
}
variable "public_subnets" {
  type    = list(string)
  default = []
}
#Availability Zone Variables
variable "azs" {
  type    = list(string)
  default = []
}

data "aws_availability_zones" "available" {
  state = "available"
}

#Local Variable Definitions
locals {
  vpc_cidr_ab          = "10.0"
  private_subnet_cidrs = 0
  max_private_subnets  = 3
  public_subnet_cidrs  = 3 //This is where the subnets will start their count from (ex: 10.0.3.0/24)
  max_public_subnets   = 3
  azs                  = data.aws_availability_zones.available.names
}

locals {
  private_subnets = [
    for az in local.azs :
    "${local.vpc_cidr_ab}.${local.private_subnet_cidrs + index(local.azs, az)}.0/24"
//    if index(local.azs, az) < local.max_private_subnets
  ]
  public_subnets = [
    for az in local.azs :
    "${local.vpc_cidr_ab}.${local.public_subnet_cidrs + index(local.azs, az)}.0/24"
    if index(local.azs, az) < local.max_public_subnets
  ]
}
