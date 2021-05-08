#Terraform: AWS_VPC Module

This module will create a VPC with the following characteristics:
- three (3) public subnets across three availability zones
- three (3) private subnets across three availability zones
- EC2, ElasticLoadBalancer, and S3 Endpoints (required for disconnected OCP4 installation)
- Internet Gateway for Public Subnets
- Route tables 
- Security Groups for endpoints

This module is intednded to be run as part of the devkit-vpc build, however if one must run it outside of devkit
they can simply use the main.tf template in the tests directory.

|variable|default|purpose|
|-----|------|------|
|vpc_name| `<none>` | Define the name of the VPC to create|
|cluster_naem| `<none>` | Define the name of the OCP cluster|
|private_subnets| `<none>`| 3 subnets will be created | This list of subnets is dynamically created|
|public_subnets | `<none>` |3 subnets will be created | This list of subnets is dynamically crated|
|azs| `<none>`| Dynamically generated list of availability zones|
|dns_support_enabled| `<true>`| Enables DNS support from the provider|
|enable_dns_hostnames|`<true>`| Allows AWS to assign a hostname using `ip-xx-xx-` synatx|
|create_public_subnets|`<true>`| Creates public subnets|
|create_private_subnets|`<true>`| Creates private subnets|


Future State:
The use for this module will morph to support IPI and UPI deployments. The idea is to provision the VPC
and a bastion (jump) node in the same VPC so an IPI installation can happen without incident.

## To Do:
- Add bastion node
- Move other modules into scaffolding 
- Document each module
- Ansible playbook to assert required vars are set and to build out terraform modules
- Keep pushing modularity 

