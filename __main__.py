import pulumi
import pulumi_aws as aws

config = pulumi.Config()

shared_vpc = aws.ec2.Vpc(
    resource_name=config.require("vpc_id"),
    assign_generated_ipv6_cidr_block=True,
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,enable_dns_support=True,
    tags={
    "Name": config.require("cluster_name"),
    "kubernetes.io/cluster/config.require("cluster_name")": "owned"
      }
    )

available = aws.get_availability_zones(state="available")

subnet_gateway = aws.ec2.Subnet(
  resource_name='pulumi-aws-example_gateway',
  availability_zone=available.names[0],
  cidr_block="10.0.4.0/24",
  vpc_id=shared_vpc.id,
  tags={
  "Name": "pulumi-aws-public"
    }
)

internet_gateway = aws.ec2.InternetGateway(
  resource_name='pulumi-aws-example',
  vpc_id=shared_vpc.id
)

gateway_eip = aws.ec2.Eip(
  resource_name='pulumi-aws-example',
  vpc=True
)

routetable_application = aws.ec2.RouteTable(
  resource_name='pulumi-aws-example_table',
  vpc_id=shared_vpc.id,
  routes=[{
    "cidrBlock": "0.0.0.0/16",
    "gatewayId": internet_gateway.id
    }]
)

route_table_association = aws.ec2.RouteTableAssociation(
  resource_name='pulumi-aws-example_association',
  subnet_id=subnet_gateway.id,
  route_table_id=routetable_application
)
