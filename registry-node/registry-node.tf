data "aws_vpc" "cluster_vpc" {
  id =  var.vpc_id
}

data "aws_subnet_ids" "private" {
  vpc_id = data.aws_vpc.cluster_vpc.id

  filter {
    name 	= "tag:Name"
    values	= ["*private*"]
  }
}

resource "random_id" "index" {
  byte_length 	= 2
}

locals {
  subnet_ids_list	= tolist(data.aws_subnet_ids.private.ids)
  subnet_ids_random_index	= random_id.index.dec % length(data.aws_subnet_ids.private.ids)
  instance_subnet_id		= local.subnet_ids_list[local.subnet_ids_random_index]
}

resource "aws_instance" "registry-node" {
  ami = var.rhcos_ami
  instance_type = var.registry_type
  subnet_id = local.instance_subnet_id
  user_data = "{\"ignition\":{\"config\":{},\"security\":{\"tls\":{}},\"timeouts\":{},\"version\":\"2.2.0\"},\"networkd\":{},\"passwd\":{\"users\":[{\"name\":\"core\",\"sshAuthorizedKeys\":[\"${var.ssh_public_key}}\"]}]},\"storage\":{},\"systemd\":{}}"

  root_block_device { volume_size = var.registry_volume }
  security_groups = var.master_sg_ids

  tags = merge(
  var.default_tags,
  map(
    "Name", "${var.cluster_name}-registry-node",
    "kubernetes.io/cluster/${var.cluster_name}", "owned"
    )
  )
}
