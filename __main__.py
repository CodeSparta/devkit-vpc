import pulumi
import pulumi_aws as aws

# Global variable API calls
config = pulumi.Config()
cluster_region = aws.get_region()
available = aws.get_availability_zones(state="available")

# Create the base VPC
shared_vpc = aws.ec2.Vpc(
    resource_name=config.require("vpc_id"),
    assign_generated_ipv6_cidr_block=True,
    cidr_block=config.require('vpc_cidr_block'),
    enable_dns_hostnames=True,enable_dns_support=True,
    tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )


# Create the public subnet
pulumi_public_subnet = aws.ec2.Subnet(
  resource_name='pulumi-public_subnet',
  availability_zone=available.names[0],
  cidr_block=config.require('public_subnet'),
  vpc_id=shared_vpc.id,
  tags={
  "Name": config.require('cluster_name') + "-public-" + available.names[0],
  "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

# Create the 3 private subnets. Thi should be ablle to be a loop in the future instead of 3 blocks
pulumi_private_subnet_a = aws.ec2.Subnet(
  resource_name='pulumi-private_subnet_a',
  availability_zone=available.names[0],
  cidr_block=config.require('private_subnet_0'),
  vpc_id=shared_vpc.id,
  tags={
  "Name": config.require('cluster_name') + "-public-" + available.names[0],
  "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

pulumi_private_subnet_b = aws.ec2.Subnet(
  resource_name='pulumi-private_subnet_b',
  availability_zone=available.names[1],
  cidr_block=config.require('private_subnet_1'),
  vpc_id=shared_vpc.id,
  tags={
  "Name": config.require('cluster_name') + "-public-" + available.names[1],
  "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

pulumi_private_subnet_c = aws.ec2.Subnet(
  resource_name='pulumi-private_subnet_c',
  availability_zone=available.names[2],
  cidr_block=config.require('private_subnet_2'),
  vpc_id=shared_vpc.id,
  tags={
  "Name": config.require('cluster_name') + "-public-" + available.names[2],
  "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

# Only needed when a public subnet and access is required
internet_gateway = aws.ec2.InternetGateway(
  resource_name='pulumi-aws-example',
  vpc_id=shared_vpc.id,
    tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
)

gateway_eip = aws.ec2.Eip(
  resource_name=config.require('cluster_name') + "-gateway",
  vpc=True,
      tags={
      "Name": config.require('cluster_name'),
      "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
        }
)

# Public route table
public_routetable = aws.ec2.RouteTable(
  resource_name=config.require('cluster_name')+ "_public_table",
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

# Private route table
private_routetable = aws.ec2.RouteTable(
  resource_name=config.require('cluster_name') + "_private_table",
  vpc_id=shared_vpc.id,
  routes=[{
    "cidrBlock": "0.0.0.0/16",
    }],
  tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

# Public routetable_association
public_route_table_association = aws.ec2.RouteTableAssociation(
  resource_name=config.require('cluster_name') + "-public-routetable_association",
  subnet_id=pulumi_public_subnet.id,
  route_table_id=public_routetable
)


private_route_table_association = aws.ec2.RouteTableAssociation(
  resource_name=config.require('cluster_name') + "-routetable_association",
  subnet_id=pulumi_public_subnet.id,
  route_table_id=private_routetable
)
