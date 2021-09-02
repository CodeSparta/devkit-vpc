import pulumi
import pulumi_aws as aws
import utils
import json
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
aws_key_string = config.require('aws_public_key')

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

private_routetable = aws.ec2.RouteTable(
    resource_name=config.require('cluster_name') + "-private-{zone}",
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

public_subnet_ids = []
private_subnet_ids = []
private_route_ids = []

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

#bastion security group
bastion_sg = aws.ec2.SecurityGroup(
    config.require('cluster_name') + "-bastion-sg",
    vpc_id=shared_vpc.id,
    description="VPC bastion SG",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],}
    ],
    tags={
        "Name": config.require('cluster_name') + "-bastion-sg",
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
    vpc_endpoint_type="Gateway",
    route_table_ids=[private_routetable.id],
    tags={
        "Name": config.require('cluster_name') + "-s3-endpoint",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# EC2 endpoint
ec2_vpc_endpoint = aws.ec2.VpcEndpoint("ec2",
    vpc_id=shared_vpc.id,
    service_name="com.amazonaws.us-gov-west-1.ec2",
    vpc_endpoint_type="Interface",
    security_group_ids=[endpoint_sg.id],
    tags={
        "Name": config.require('cluster_name') + "-ec2-endpoint",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

sn_ec2 = list()  # define variable in global scope
for index, priv_subnet_id in enumerate(private_subnet_ids):
    result = aws.ec2.VpcEndpointSubnetAssociation(f"snEc2_{index}",
        vpc_endpoint_id=ec2_vpc_endpoint.id,
        subnet_id=priv_subnet_id
        )
    sn_ec2.append(result)

# ELB endpoint
elb_vpc_endpoint = aws.ec2.VpcEndpoint("elb",
    vpc_id=shared_vpc.id,
    service_name="com.amazonaws.us-gov-west-1.elasticloadbalancing",
    vpc_endpoint_type="Interface",
    security_group_ids=[endpoint_sg.id],
    tags={
        "Name": config.require('cluster_name') + "-elb-endpoint",
        "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

sn_elb = list()  # define variable in global scope
for index, priv_subnet_id in enumerate(private_subnet_ids):
    result = aws.ec2.VpcEndpointSubnetAssociation(f"snelb_{index}",
        vpc_endpoint_id=elb_vpc_endpoint.id,
        subnet_id=priv_subnet_id
        )
    sn_elb.append(result)

# Create IAM Roles, Policies and attachements
master_role = aws.iam.Role("master_role",
  name=config.require('cluster_name') + "-master-role",
  assume_role_policy=json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
      }],
  }),
  tags={
    "Name": config.require('cluster_name') + "-master-role",
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

worker_role = aws.iam.Role("worker_role",
  name=config.require('cluster_name') + "-worker-role",
  assume_role_policy=json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
      }],
  }),
  tags={
    "Name": config.require('cluster_name') + "-worker-role",
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

worker_policy = aws.iam.RolePolicy("worker_policy",
    role=worker_role.id,
    name=config.require('cluster_name') + "-worker-policy",
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:Describe*",
      "Resource": "*"
      }],
          }))

master_policy = aws.iam.RolePolicy("master_policy",
    role=master_role.id,
    name=config.require('cluster_name') + "-master-policy",
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
        {
        "Action": "ec2:*",
        "Resource": "*",
        "Effect": "Allow"
        },
        {
        "Action": "iam:PassRole",
        "Resource": "*",
        "Effect": "Allow"
        },
        {
        "Action" : [
        "s3:GetObject"
        ],
        "Resource": "*",
        "Effect": "Allow"
            },
            {
        "Action": "elasticloadbalancing:*",
        "Resource": "*",
        "Effect": "Allow",
            }],
    }))

master_instance_profile = []
worker_instance_profile = []

master_profile = aws.iam.InstanceProfile("masterProfile",
  name=config.require('cluster_name') + "-master-profile",
  role=master_role.id
  )

worker_profile = aws.iam.InstanceProfile("workerProfile",
  name=config.require('cluster_name') + "-worker-profile",
  role=worker_role.id
  )

master_instance_profile.append(master_profile.id)
worker_instance_profile.append(worker_profile.id)


# Create bastion node

bastion_host=aws.ec2.Instance("bastion",
    ami=config.require('rhel8_ami'),
    instance_type=config.require('bastion_type'),
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[bastion_sg.id],
    key_name=config.require('aws_ssh_key'),
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_size=120,
        volume_type="gp3"
    ),
  tags={
    "Name": config.require('cluster_name') + "-bastion",
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# Create coreos registry node

registry_host=aws.ec2.Instance("registry",
    ami=config.require('rhcos_ami'),
    instance_type=config.require('bastion_type'),
    subnet_id=private_subnet.id,
    vpc_security_group_ids=[master_sg.id],
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_size=120,
        volume_type="gp3"
    ),
    user_data={"ignition": {"version":"3.1.0"},"passwd":{"users":[{"name": "core","passwordHash": "","sshAuthorizedKeys":[config.require('aws_public_key')]}]}},
  tags={
    "Name": config.require('cluster_name') + "-registry-node",
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

# Create route53 private hosted zone with registry record
private_route53_zone = aws.route53.Zone("private",
    name=config.require('cluster_name') + "." + config.require('cluster_domain'),
    vpcs=[aws.route53.ZoneVpcArgs(
      vpc_id=shared_vpc.id
      )],
  tags={
    "Name": config.require('cluster_name') + "." + config.require('cluster_domain'),
    "kubernetes.io/cluster/" + config.require('cluster_name'): "owned"
      }
    )

registry_record = aws.route53.Record("registry-record",
    zone_id=private_route53_zone.id,
    name="registry",
    type="A",
    ttl=300,
    records=[registry_host.private_ip]
)


pulumi.export("pulumi-az-amount", zones_amount)
pulumi.export("pulumi-vpc-id", shared_vpc.id)
pulumi.export("pulumi-public-subnet-ids", public_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
pulumi.export("pulumi-private-subnet-ids", private_subnet_ids)
pulumi.export("pulumi-master-instance-profile", master_instance_profile)
pulumi.export("pulumi-worker-instance-profile", worker_instance_profile)
