data "aws_vpc" "cluster_vpc" {
    id =  var.vpc_id
  }

data "aws_subnet" "master-subnets" {
  filter {
    name   = "tag:Name"
    values = [format("${var.cluster_name}-private-%s", format("%s%s", var.aws_region, element(var.aws_azs, 0)))]
}
}
