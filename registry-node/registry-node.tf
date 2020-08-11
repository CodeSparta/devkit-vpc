resource "aws_instance" "registry-node" {
  ami = var.rhcos_ami
  instance_type = var.registry_type
  subnet_id = aws_subnet.private-subnet.id
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

resource "aws_subnet" "private-subnet" {
  vpc_id = data.aws_vpc.cluster_vpc.id
  cidr_block = var.vpc_private_subnet_cidrs[0]
  availability_zone = format("%s%s", element(list(var.aws_region), 0), element(var.aws_azs, 0))
  map_public_ip_on_launch = true
}

