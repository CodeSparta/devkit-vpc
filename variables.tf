variable "cidr_blocks" { default = "10.0.0.0/16"}
variable "cluster_name" { default = "" }
variable "aws_region" { default = "us-gov-west-1" }
variable "default_tags" { default = {} }
variable "aws_azs" { default = ["a", "b", "c"] }
variable "vpc_private_subnet_cidrs" { default = ["10.0.1.0/24","10.0.2.0/24","10.0.3.0/24"] }
variable "vpc_public_subnet_cidrs" { default = ["10.0.7.0/26", "10.0.8.0/26", "10.0.9.0/26"] }
variable "aws_access_key" { default = ""}
variable "aws_secret_key" { default = ""}
variable "vpc_id" {
  description = "The VPC used to create the private route53 zone."
}