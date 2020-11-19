// Declare Preconfigured AWS Account SSH Private Key Name
// https://docs.aws.amazon.com/ground-station/latest/ug/create-ec2-ssh-key-pair.html
variable "aws_ssh_key" {default = ""}


// COPY & PASTE full id-rsa string.
// For example cat ~/.ssh/id_rsa.pub or your key of choice
variable "ssh_public_key" {
  type = string
  default = "public_key_string"
}

// Set RH CoreOS AMI ID
variable "rhcos_ami" {default = ""}

// VPC & Domain Naming
// Ensure vpc_id and cluster_name are the same
variable "vpc_id" { default = "sparta" }
variable "cluster_name" { default = "sparta" }
variable "cluster_domain" { default = "redhat.io" }

// Instance Config
variable "bastion_ami" {default = "ami-d281d2b3"}
