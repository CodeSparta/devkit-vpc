data "aws_vpc" "cluster_vpc" {
  id =  var.vpc_id
}

data "aws_subnet" "master-subnets" {
  filter {
    name   = "tag:Name"
    values = [format("${var.cluster_name}-public-%s", format("%s%s", var.aws_region, element(var.aws_azs, 0)))]
  }
}


resource "aws_instance" "bastion-node" {
  ami           = var.bastion_ami
  instance_type = var.bastion_type
  key_name      = var.aws_key
  subnet_id     = data.aws_subnet.master-subnets.id

  root_block_device { volume_size = var.bastion_disk }

  tags = merge(
  var.default_tags,
  map(
    "Name", "${var.cluster_name}-bastion-node"
    )
  )
}