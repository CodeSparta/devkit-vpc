# Development-IaC
### First Rule of DevKit [we dont talk about devkit](https://www.urbandictionary.com/define.php?term=fight%20club)    
### [DISCLAIMER](https://github.com/CodeSparta/devkit-vpc/blob/master/DISCLAIMER.md)    

## Summary
This terraform play is designed to create a working development VPC for the user. It will create the following resources:

- Three Public subnets
- Three Private subnets "no nat to simulate airgapped"
- s3 vpc\_endpoint
- ec2 vpc\_endpoint
- elb vpc\_endpoint
- sts vpc\_endpoint
- Route 53 private zone
- Security Groups
- Bastion ec2 Instance
- Registry ec2 Instance

## Requirement
- Aws ssh key for the bastion
- AMI Ids for Rhel 8 and Rhcos images

## Usage:
#### Step 01 - Download the git to your local machine:
```
 git clone --branch 4.5.6 https://github.com/CodeSparta/devkit-vpc.git && cd devkit-vpc
```
#### Step 02 - Setup your variables.tf
```
vi variables.tf
```
#### Step 03 - Exec into the container and deploy
```
bash tools/dev.sh
./devkit-build-vpc.sh -vv -e aws_access_key=xxxxxxxxxxxxx -e aws_secret_key=XXXXXXXXXXXXXXXXX -e aws_cloud_region=us-gov-west-1
```
-------------------------------------------------------------------
## Teardown:
#### Step 03 - Exec into the container and deploy
To destroy the IaC run:
```
cd into git repo
source tools/dev.sh
./breakdown.yml -vv
```
All resources not created from the IaC must be deleted prior to destroying the vpc.
