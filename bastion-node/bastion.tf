data "aws_vpc" "cluster_vpc" {
  id =  var.vpc_id
}
resource "aws_instance" "bastion-node" {
  ami           = var.bastion_ami
  instance_type = var.bastion_type
  subnet_id     = aws_subnet.bastion-pub-subnet.id
  key_name      = var.aws_key
  root_block_device { volume_size = var.bastion_disk }

  tags = merge(
  var.default_tags,
  map(
  "Name", "${var.cluster_name}-bastion-node"
    )
  )
}

resource "aws_subnet" "bastion-pub-subnet" {
  vpc_id                  = data.aws_vpc.cluster_vpc.id
  cidr_block              = var.vpc_public_subnet_cidrs[0]
  availability_zone       = format("%s%s", element(list(var.aws_region), 0), element(var.aws_azs, 0))
  map_public_ip_on_launch = true
}