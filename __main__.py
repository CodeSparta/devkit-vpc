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
    "cidrBlock":  "0.0.0.0/0",
    "gatewayId": internet_gateway.id
    }],
  tags={
    "Name": config.require('cluster_name') + "-public",
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

# Create Private subenet, route table and append instances
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
          "cidr_block": "0.0.0.0/16",
          "gatewayId": internet_gateway.id
          }],
        tags={
            "Name": config.require('cluster_name') + "-private",
            "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

    aws.ec2.RouteTableAssociation(
        f"{cluster_name}-private-rta-{zone}",
        route_table_id=private_routetable.id,
        subnet_id=private_subnet.id,
    )
    private_subnet_ids.append(private_subnet.id)

# Create security groups

# VPC endpoint security group
endpoint_sg = aws.ec2.SecurityGroup(
    config.require('cluster_name') + "endpoint-sg",
    vpc_id=shared_vpc.id,
    description="VPC endpoint SG",
    ingress=[
        {
            "protocol": "all",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],}
    ],
    tags={
        "Name": config.require('cluster_name') + "-endpoint-sg",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# boostrap security group
bootstrap_sg = aws.ec2.SecurityGroup(
    config.require('cluster_name') + "bootstrap-sg",
    vpc_id=shared_vpc.id,
    description="VPC bootstrap SG",
    ingress=[
        {
            "protocol": "all",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],}
    ],
    tags={
        "Name": config.require('cluster_name') + "-bootstrap-sg",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# master security group
master_sg = aws.ec2.SecurityGroup(
    config.require('cluster_name') + "master-sg",
    vpc_id=shared_vpc.id,
    description="VPC master SG",
    ingress=[
        {
            "protocol": "all",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],}
    ],
    tags={
        "Name": config.require('cluster_name') + "-master-sg",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )
# worker security group
worker_sg = aws.ec2.SecurityGroup(
    config.require('cluster_name') + "worker-sg",
    vpc_id=shared_vpc.id,
    description="VPC worker SG",
    ingress=[
        {
            "protocol": "all",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],}
    ],
    tags={
        "Name": config.require('cluster_name') + "-worker-sg",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# Create VPC endpoints

# S3 endpoint
s3_vpc_endpoint = aws.ec2.VpcEndpoint("s3",
    vpc_id=shared_vpc.id,
    service_name="com.amazonaws.us-gov-west-1.s3",
#    route_table_ids =
#    security_group_ids=endpoint_sg.id,
    tags={
        "Name": config.require('cluster_name') + "-s3-endpoint",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )
# EC2 endpoint
ec2_vpc_endpoint = aws.ec2.VpcEndpoint("ec2",
    vpc_id=shared_vpc.id,
    service_name="com.amazonaws.us-gov-west-1.ec2",
#    subnet_ids=private_subnet_ids.id,
    security_group_ids=endpoint_sg.id,
    tags={
        "Name": config.require('cluster_name') + "-ec2-endpoint",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# ELB endpoint
elb_vpc_endpoint = aws.ec2.VpcEndpoint("ec2",
    vpc_id=shared_vpc.id,
    service_name="com.amazonaws.us-gov-west-1.elasticloadbalancing",
#    subnet_ids=private_subnet_ids.id,
    security_group_ids=endpoint_sg.id,
    tags={
        "Name": config.require('cluster_name') + "-elb-endpoint",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )



pulumi.export("pulumi-az-amount", zones_amount)
pulumi.export("pulumi-vpc-id", shared_vpc.id)
pulumi.export("pulumi-public-subnet-ids", public_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
