
resource "aws_instance" "registry-node" {
  ami = var.rhcos_ami
  instance_type = var.registry_type
  subnet_id = data.aws_subnet.master-subnets.id
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

