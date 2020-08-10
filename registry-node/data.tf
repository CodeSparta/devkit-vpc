data "aws_vpc" "cluster_vpc" {
  id =  var.vpc_id
}

data "aws_route53_zone" "route53-zone" {
  name = "${var.cluster_name}.${var.cluster_domain}"
  private_zone = true
}