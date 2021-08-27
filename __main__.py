import pulumi
import pulumi_aws as aws
import utils

# Global variable API calls
config = pulumi.Config()

cluster_region = aws.get_region()
available = aws.get_availability_zones(state="available")
public_subnet_cidrs = config.require_object("public_subnet_cidrs")
private_subnet_cidrs = config.require_object("private_subnet_cidrs")
cluster_name = config.require('cluster_name')
zones_amount = config.require_int("zones_amount")
zones = utils.get_aws_az(zones_amount)
vpc_cidr_block = config.require('vpc_cidr_block')

# Create the base VPC
shared_vpc = aws.ec2.Vpc(
    resource_name=config.require("vpc_id"),
    assign_generated_ipv6_cidr_block=True,
    cidr_block=config.require('vpc_cidr_block'),
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# Only needed when a public subnet and access is required
internet_gateway = aws.ec2.InternetGateway(
  resource_name=config.require('cluster_name') + "-igw",
  vpc_id=shared_vpc.id,
    tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
)

# Public gateway EIP
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
    "cidrBlock":  "{vpc_cidr_block}",
    "gatewayId": internet_gateway.id
    }],
  tags={
    "Name": config.require('cluster_name'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
    }
)

public_subnet_ids = []
private_subnet_ids = []

# Create Public subnets and routes
for zone, public_subnet_cidr, private_subnet_cidr in zip(
    zones, private_subnet_cidrs, public_subnet_cidrs
):
    public_subnet = aws.ec2.Subnet(
        f"{cluster_name}-public-subnet-{zone}",
        assign_ipv6_address_on_creation=False,
        vpc_id=shared_vpc.id,
        map_public_ip_on_launch=True,
        cidr_block=public_subnet_cidr,
        availability_zone=zone,
        tags={
        "Name": f"{cluster_name}-public-subnet-{zone}",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
        },

    )
    aws.ec2.RouteTableAssociation(
        f"{cluster_name}-public-rta-{zone}",
        route_table_id=public_routetable.id,
        subnet_id=public_subnet.id,
    )

    public_subnet_ids.append(public_subnet.id)

    private_subnet = aws.ec2.Subnet(
        f"{cluster_name}-private-subnet-{zone}",
        assign_ipv6_address_on_creation=False,
        vpc_id=shared_vpc.id,
        map_public_ip_on_launch=False,
        cidr_block=private_subnet_cidr,
        availability_zone=zone,
        tags={
        "Name": f"{cluster_name}-private-subnet-{zone}",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
        },
    )

    private_routetable = aws.ec2.RouteTable(
        f"{cluster_name}-private-{zone}",
        vpc_id=shared_vpc.id,
        routes=[{
          "cidr_block": "{vpc_cidr_block}"
          }],
        tags={
            "Name": config.require('cluster_name'),
            "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

    aws.ec2.RouteTableAssociation(
        f"{cluster_name}-private-rta-{zone}",
        route_table_id=private_routetable.id,
        subnet_id=private_subnet.id,
    )
    private_subnet_ids.append(private_subnet.id)


pulumi.export("pulumi-az-amount", zones_amount)
pulumi.export("pulumi-vpc-id", shared_vpc.id)
pulumi.export("pulumi-public-subnet-ids", public_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
