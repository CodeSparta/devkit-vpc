// Set aws keys
variable "aws_access_key" { default = "xxxxxxxxxx"}
variable "aws_secret_key" { default = "XXXXXXXXXX"}
variable "aws_region" { default = "us-gov-west-1" }

// Declare Preconfigured AWS Account SSH Private Key Name
// https://docs.aws.amazon.com/ground-station/latest/ug/create-ec2-ssh-key-pair.html
variable "aws_ssh_key" { default = "aws_acct_key_name"}

// COPY & PASTE full id-rsa string.
// For example cat ~/.ssh/id_rsa.pub or your key of choice
variable "ssh_public_key" {default = "" }

// Set RH CoreOS AMI ID
variable "rhcos_ami" {default = ""}

// VPC & Domain Naming
variable "vpc_id" { default = "sparta" }
variable "cluster_name" { default = "sparta" }
variable "cluster_domain" { default = "sparta.cloud.dev" }

/*
  END USER CUSTOMIZATION
*/

// General Defaults
variable "default_tags" { default = {} }
variable "aws_azs" { default = ["a", "b", "c"] }
variable "cidr_blocks" { default = "10.0.0.0/16"}
variable "vpc_private_subnet_cidrs" { default = ["10.0.1.0/24","10.0.2.0/24","10.0.3.0/24"] }
variable "vpc_public_subnet_cidrs" { default = ["10.0.7.0/26", "10.0.8.0/26", "10.0.9.0/26"] }

// Instance Config
variable "bastion_ami" {default = "ami-d281d2b3"}
variable "bastion_type" {default = "t2.xlarge"}
variable "registry_type" {default = "m5.xlarge"}
variable "bastion_disk" {default = "100"}
variable "registry_volume" {default = "120"}
variable "public_subnet_id" { default = "" }
variable "master_sg_ids" {default = "" }
