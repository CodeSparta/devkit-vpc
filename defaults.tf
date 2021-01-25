// General Defaults
variable "default_tags" { default = {} }
variable "aws_azs" { default = ["a", "b", "c"] }
variable "cidr_blocks" { default = "10.0.0.0/16"}
variable "vpc_private_subnet_cidrs" { default = ["10.0.1.0/24","10.0.2.0/24","10.0.3.0/24"] }
variable "vpc_public_subnet_cidrs" { default = ["10.0.7.0/26", "10.0.8.0/26", "10.0.9.0/26"] }

// Instance Config
variable "bastion_type" {default = "m5.xlarge"}
variable "registry_type" {default = "m5.xlarge"}
variable "bastion_disk" {default = "100"}
variable "registry_volume" {default = "120"}
variable "public_subnet_id" { default = "" }
variable "master_sg_ids" {default = "" }

// Defaults are written to credentials leave blank
variable "aws_access_key" { default = "xxxxxxxxxx"}
variable "aws_secret_key" { default = "XXXXXXXXXX"}
variable "aws_region" { default = "" }
