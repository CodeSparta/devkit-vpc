from pulumi_aws import get_availability_zones

def get_aws_az(amount):
    zones = get_availability_zones()
    return zones.names[:amount]
