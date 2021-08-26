import pulumi
import pulumi_aws as aws

config = pulumi.Config()
cluster_region = aws.get_region()

shared_vpc = aws.ec2.Vpc(
    resource_name=config.require("vpc_id"),
    assign_generated_ipv6_cidr_block=True,
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,enable_dns_support=True,
    tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

available = aws.get_availability_zones(state="available")

pulumi_public_subnet = aws.ec2.Subnet(
  resource_name='pulumi-public_subnet',
  availability_zone=available.names[0],
  cidr_block="10.0.4.0/24",
  vpc_id=shared_vpc.id,
  tags={
  "Name": config.require('cluster_name') + "-public-" + available.names[0],
  "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

internet_gateway = aws.ec2.InternetGateway(
  resource_name='pulumi-aws-example',
  vpc_id=shared_vpc.id,
    tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
)

gateway_eip = aws.ec2.Eip(
  resource_name='pulumi-aws-example',
  vpc=True,
      tags={
      "Name": config.require('cluster_name'),
      "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
        }
)

public_routetable = aws.ec2.RouteTable(
  resource_name='pulumi-public_table',
  vpc_id=shared_vpc.id,
  routes=[{
    "cidrBlock": "0.0.0.0/16",
    "gatewayId": internet_gateway.id
    }],
  tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

route_table_association = aws.ec2.RouteTableAssociation(
  resource_name='pulumi-routetable_association',
  subnet_id=subnet_gateway.id,
  route_table_id=public_routetable,
     tags={
      "Name": config.require('cluster_name'),
      "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
        }
)
